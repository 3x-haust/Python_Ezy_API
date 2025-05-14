"""
API 코어 모듈

이 모듈은 Ezy API의 핵심 클래스와 기능을 제공합니다.
"""

import inspect
import os
import re
from typing import Any, Dict, Type, get_type_hints, Optional, Callable
from fastapi import APIRouter, Depends, FastAPI, Path, Query, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ezyapi.service.base import EzyService
from ezyapi.database.config import DatabaseConfig, auto_inject_repository
from ezyapi.utils.inflection import get_service_name

class EzyAPI:
    """
    Ezy API의 핵심 클래스
    
    이 클래스는 서비스 등록, 라우팅 설정, API 서버 실행 등을 담당합니다.
    """
    
    def __init__(self, 
                 title: str = "EzyAPI", 
                 description: str = "Auto-generated API from services",
                 db_config: Optional[DatabaseConfig] = None):
        """
        EzyAPI 클래스 초기화
        
        Args:
            title (str): API 제목, OpenAPI 문서에 표시됨
            description (str): API 설명, OpenAPI 문서에 표시됨
            db_config (Optional[DatabaseConfig]): 데이터베이스 설정 객체
        """
        self.app = FastAPI(title=title, description=description)
        self.services: Dict[str, Type[EzyService]] = {}
        self.db_config = db_config
        
        current_dir = os.getcwd()
        self.templates_dir = os.path.join(current_dir, "public", "templates")
        static_dir = os.path.join(current_dir, "public")
        
        if os.path.exists(static_dir):
            self.app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    def configure_database(self, db_config: DatabaseConfig):
        """
        데이터베이스 설정을 구성합니다.
        
        Args:
            db_config (DatabaseConfig): 데이터베이스 설정 객체
            
        Returns:
            EzyAPI: 메소드 체이닝을 위한 자기 자신
            
        Raises:
            TypeError: db_config가 DatabaseConfig 인스턴스가 아닌 경우
        """
        if not isinstance(db_config, DatabaseConfig):
            raise TypeError("db_config는 DatabaseConfig 인스턴스여야 합니다.")
        self.db_config = db_config
        return self

    def add_service(self, service_class: Type[EzyService]) -> None:
        """
        API에 서비스를 등록합니다.
        
        Args:
            service_class (Type[EzyService]): 등록할 서비스 클래스
            
        Raises:
            TypeError: service_class가 EzyService의 하위 클래스가 아닌 경우
        """
        if not issubclass(service_class, EzyService):
            raise TypeError(f"{service_class.__name__}는 EzyService를 상속받아야 합니다.")
        
        service_name = get_service_name(service_class)
        self.services[service_name] = service_class
        router = self._create_router_from_service(service_class, service_name)
        
        self.app.include_router(router, tags=[service_name])
    
    def _load_html_template(self, template_name: str) -> str:
        """
        HTML 템플릿 파일을 로드합니다.
        
        Args:
            template_name (str): 로드할 템플릿 파일 이름
            
        Returns:
            str: 템플릿 파일 내용
            
        Raises:
            FileNotFoundError: 템플릿 파일이 존재하지 않는 경우
        """
        template_path = os.path.join(self.templates_dir, template_name)
        if not os.path.exists(template_path):
            raise FileNotFoundError(f"템플릿 파일을 찾을 수 없습니다: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def _create_router_from_service(self, service_class: Type[EzyService], service_name: str) -> APIRouter:
        """
        서비스 클래스로부터 FastAPI 라우터를 생성합니다.
        
        서비스 클래스의 메소드를 분석하여 HTTP 엔드포인트로 등록합니다.
        
        Args:
            service_class (Type[EzyService]): 라우터를 생성할 서비스 클래스
            service_name (str): 서비스 이름
            
        Returns:
            APIRouter: 생성된 FastAPI 라우터
            
        Raises:
            RuntimeError: 라우팅 규칙 충돌 또는 메소드 이름 규칙 위반 시
        """
        router = APIRouter()
        service_instance = auto_inject_repository(service_class, self.db_config)
        existing_routes = {}

        for method_name, method in inspect.getmembers(service_class, inspect.isfunction):
            if method_name.startswith('_'):
                continue

            method_parts = method_name.split('_')
            
            if method_parts[0] == 'list':
                expected_name = f'list_{service_name}s'
                if method_name != expected_name:
                    raise RuntimeError(
                        f"목록 메소드 이름 규칙 오류: '{method_name}'이 아닌 '{expected_name}'(으)로 이름을 지정해야 합니다."
                    )
            elif service_name not in method_name:
                raise RuntimeError(
                    f"메소드 이름 규칙 오류: '{method_name}'에는 서비스 이름 '{service_name}'이(가) 포함되어야 합니다."
                )

            custom_route = getattr(method, '__route_info__', None)
            if custom_route:
                http_method = custom_route['method']
                path = custom_route['path']
                extra_kwargs = custom_route['extra_kwargs']
            else:
                http_method, path = self._parse_method_name(method_name, service_name)
                extra_kwargs = {}

            if service_name == "app" and path == "":
                path = "/"

            if http_method in existing_routes:
                for existing_path in existing_routes[http_method]:
                    if self._is_conflicting_path(existing_path, path):
                        raise RuntimeError(
                            f"라우트 충돌 감지: '{http_method.upper()} {path}'이(가) "
                            f"기존 라우트 '{http_method.upper()} {existing_path}'와(과) 충돌합니다. "
                            "메소드 이름을 변경하거나 고유한 라우트를 지정하세요."
                        )
            existing_routes.setdefault(http_method, []).append(path)

            params = inspect.signature(method).parameters
            return_type = get_type_hints(method).get('return', Any)

            request_body = None
            path_params = []
            query_params = {}
            param_types = {}

            for param_name, param in params.items():
                if param_name == 'self':
                    continue
                param_type = get_type_hints(method).get(param_name, Any)
                param_types[param_name] = param_type
                if inspect.isclass(param_type) and issubclass(param_type, BaseModel):
                    request_body = param_type
                elif '{' + param_name + '}' in path:
                    path_params.append(param_name)
                else:
                    default_value = param.default if param.default is not param.empty else None
                    query_params[param_name] = {
                        'type': param_type,
                        'default': default_value,
                        'required': param.default is param.empty and param.annotation != Optional[param_type.__args__[0]] if hasattr(param_type, '__args__') else True
                    }

            if request_body:
                async def endpoint_with_body(
                    data: request_body,
                    service_instance=service_instance, 
                    method=method,
                    path_params=path_params
                ):
                    call_args = {'data': data}
                    
                    for param in path_params:
                        call_args[param] = self._convert_param_type(
                            request.path_params.get(param), 
                            param_types.get(param, Any)
                        )
                    
                    result = await method(service_instance, **call_args)
                    if isinstance(result, str) and result.endswith('.html') and os.path.exists(self.templates_dir):
                        template_content = self._load_html_template(result)
                        return HTMLResponse(content=template_content)
                    return result
                func = endpoint_with_body
            elif path_params or query_params:
                async def endpoint_with_params(request: Request, service_instance=service_instance, method=method, 
                                            path_params=path_params, query_params=query_params, param_types=param_types):
                    call_args = {}
                    
                    for param in path_params:
                        call_args[param] = self._convert_param_type(request.path_params.get(param), param_types.get(param, Any))
                    
                    for param_name, param_info in query_params.items():
                        value = request.query_params.get(param_name)
                        if value is not None:
                            call_args[param_name] = self._convert_param_type(value, param_info['type'])
                        elif not param_info['required']:
                            call_args[param_name] = param_info['default']
                        elif param_info['required']:
                            if param_info['type'] == Optional:
                                call_args[param_name] = None
                            else:
                                raise HTTPException(status_code=422, detail=f"필수 쿼리 매개변수가 없습니다: {param_name}")
                    
                    result = await method(service_instance, **call_args)
                    if isinstance(result, str) and result.endswith('.html') and os.path.exists(self.templates_dir):
                        template_content = self._load_html_template(result)
                        return HTMLResponse(content=template_content)
                    return result
                func = endpoint_with_params
            else:
                async def simple_endpoint(service_instance=service_instance, method=method):
                    result = await method(service_instance)
                    if isinstance(result, str) and result.endswith('.html') and os.path.exists(self.templates_dir):
                        template_content = self._load_html_template(result)
                        return HTMLResponse(content=template_content)
                    return result
                func = simple_endpoint

            func.__name__ = method_name

            is_html_template = return_type == str
            
            route = getattr(router, http_method)(
                path,
                response_model=None if is_html_template else (return_type if return_type != Any else None),
                summary=method.__doc__.strip() if method.__doc__ else method_name,
                **extra_kwargs
            )
            route(func)

        return router

    def _parse_method_name(self, method_name: str, service_name: str) -> tuple:
        """
        메소드 이름을 분석하여 HTTP 메소드와 경로를 결정합니다.
        
        Args:
            method_name (str): 서비스 메소드 이름
            service_name (str): 서비스 이름
            
        Returns:
            tuple: (HTTP 메소드, 경로)
        """
        http_methods = {
            'get': 'get',
            'list': 'get',
            'create': 'post',
            'update': 'put',
            'edit': 'patch',
            'delete': 'delete'
        }
        
        method_parts = method_name.split('_')
        http_method = http_methods.get(method_parts[0], 'get')
        
        path = ""
        
        if '_by_' in method_name:
            by_index = method_parts.index('by')
            if by_index < len(method_parts) - 1:
                param_name = method_parts[by_index + 1]
                path = f"/{{{param_name}}}"
        
        if service_name != "app" and not path.startswith(f"/{service_name}"):
            if path.startswith("/{"):
                path = f"/{service_name}" + path
            else:
                path = f"/{service_name}" + (path if path else "")
        
        return http_method, path
    
    def _is_conflicting_path(self, path1: str, path2: str) -> bool:
        """
        두 경로가 충돌하는지 확인합니다.
        
        Args:
            path1 (str): 첫 번째 경로
            path2 (str): 두 번째 경로
            
        Returns:
            bool: 경로가 충돌하면 True, 그렇지 않으면 False
        """
        def path_to_regex(path: str) -> str:
            return re.sub(r'\{[^}]+\}', r'[^/]+', path)
        return re.fullmatch(path_to_regex(path1), path2) or re.fullmatch(path_to_regex(path2), path1)
    
    def _convert_param_type(self, value: Any, param_type: Type) -> Any:
        """
        문자열 값을 지정된 유형으로 변환합니다.
        
        Args:
            value (Any): 변환할 값
            param_type (Type): 대상 유형
            
        Returns:
            Any: 변환된 값
        """
        if param_type == int:
            return int(value)
        elif param_type == float:
            return float(value)
        elif param_type == bool:
            return value.lower() in ('true', 'yes', '1')
        return value
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, reload: bool = False, **kwargs):
        """
        API 서버를 실행합니다.
        
        Args:
            host (str): 바인딩할 호스트
            port (int): 바인딩할 포트
            reload (bool): 코드 변경 시 자동 재시작 여부 (개발 모드)
            **kwargs: uvicorn에 전달할 추가 매개변수
        """
        import uvicorn
        import inspect
        import sys
        
        if reload:
            main_module = sys.modules['__main__']
            main_file = inspect.getfile(main_module)
            module_name = main_module.__name__
            
            app_var_name = None
            for var_name, var_val in vars(main_module).items():
                if var_val is self:
                    app_var_name = var_name
                    break
            
            if not app_var_name:
                raise RuntimeError(
                    "reload=True를 사용하기 위해서는 EzyAPI 인스턴스가 __main__ 모듈에서 전역 변수로 정의되어야 합니다."
                )
            
            app_import_string = f"{module_name}:{app_var_name}.app"
            uvicorn.run(app_import_string, host=host, port=port, reload=reload, **kwargs)
        else:
            uvicorn.run(self.app, host=host, port=port, **kwargs)