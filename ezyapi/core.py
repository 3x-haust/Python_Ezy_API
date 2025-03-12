import inspect
import re
from typing import Any, Dict, Type, get_type_hints, Optional, Callable
from fastapi import APIRouter, Depends, FastAPI, Path, Query, Request, HTTPException
from pydantic import BaseModel
import inflect
from functools import wraps

from ezyapi.database import EzyService, DatabaseConfig, auto_inject_repository

p = inflect.engine()

def route(method: str, path: str, **kwargs):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        wrapper.__route_info__ = {
            'method': method.lower(),
            'path': path,
            'extra_kwargs': kwargs
        }
        return wrapper
    return decorator

class EzyAPI:
    def __init__(self, 
                 title: str = "EzyAPI", 
                 description: str = "Auto-generated API from services",
                 db_config: Optional[DatabaseConfig] = None):
        self.app = FastAPI(title=title, description=description)
        self.services: Dict[str, Type[EzyService]] = {}
        self.db_config = db_config
    
    def configure_database(self, db_config: DatabaseConfig):
        if not isinstance(db_config, DatabaseConfig):
            raise TypeError("db_config must be an instance of DatabaseConfig")
        self.db_config = db_config
        return self

    def add_service(self, service_class: Type[EzyService]) -> None:
        if not issubclass(service_class, EzyService):
            raise TypeError(f"{service_class.__name__} must inherit from EzyService")
        
        service_name = self._get_service_name(service_class)
        self.services[service_name] = service_class
        router = self._create_router_from_service(service_class, service_name)
        
        prefix = "" if service_name == "app" else f"/{service_name}"
        self.app.include_router(router, prefix=prefix, tags=[service_name])

    def _get_service_name(self, service_class: Type[EzyService]) -> str:
        name = service_class.__name__
        if name.endswith("Service"):
            name = name[:-7]
        return p.singular_noun(name.lower()) or name.lower()
    
    def _create_router_from_service(self, service_class: Type[EzyService], service_name: str) -> APIRouter:
        router = APIRouter()
        service_instance = auto_inject_repository(service_class, self.db_config)
        existing_routes = {}

        for method_name, method in inspect.getmembers(service_class, inspect.isfunction):
            if method_name.startswith('_'):
                continue

            custom_route = getattr(method, '__route_info__', None)
            if custom_route:
                http_method = custom_route['method']
                path = custom_route['path']
                extra_kwargs = custom_route['extra_kwargs']
            else:
                http_method, path = self._parse_method_name(method_name)
                extra_kwargs = {}

            if service_name == "app" and path == "":
                path = "/"

            if http_method in existing_routes:
                for existing_path in existing_routes[http_method]:
                    if self._is_conflicting_path(existing_path, path):
                        raise RuntimeError(
                            f"Route conflict detected: '{http_method.upper()} {path}' "
                            f"conflicts with existing route '{http_method.upper()} {existing_path}'. "
                            "Rename one of the methods or specify distinct routes."
                        )
            existing_routes.setdefault(http_method, []).append(path)

            params = inspect.signature(method).parameters
            return_type = get_type_hints(method).get('return', Any)

            request_body = None
            path_params = []
            query_params = []
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
                    query_params.append(param_name)

            if request_body:
                async def endpoint_with_body(data: request_body, service_instance=service_instance, method=method):
                    return await method(service_instance, data=data)
                func = endpoint_with_body
            elif path_params:
                async def endpoint_with_path(request: Request, service_instance=service_instance, method=method, path_params=path_params, param_types=param_types):
                    call_args = {param: self._convert_param_type(request.path_params.get(param), param_types.get(param, Any)) for param in path_params}
                    return await method(service_instance, **call_args)
                func = endpoint_with_path
            else:
                async def simple_endpoint(service_instance=service_instance, method=method):
                    return await method(service_instance)
                func = simple_endpoint

            func.__name__ = method_name

            route = getattr(router, http_method)(
                path,
                response_model=return_type if return_type != Any else None,
                summary=method.__doc__.strip() if method.__doc__ else method_name,
                **extra_kwargs
            )
            route(func)

        return router

    
    def _parse_method_name(self, method_name: str) -> tuple:
        http_methods = {
            'get': 'get', 'find': 'get', 'retrieve': 'get', 'list': 'get',
            'create': 'post', 'add': 'post', 'update': 'put',
            'edit': 'patch', 'modify': 'patch',
            'delete': 'delete', 'remove': 'delete'
        }
        
        method_parts = method_name.split('_')
        http_method = http_methods.get(method_parts[0], 'get')
        path = ""
        if '_by_' in method_name:
            by_index = method_parts.index('by')
            if by_index < len(method_parts) - 1:
                param_name = method_parts[by_index + 1]
                path = f"/{{{param_name}}}"
        return http_method, path
    
    def _is_conflicting_path(self, path1: str, path2: str) -> bool:
        def path_to_regex(path: str) -> str:
            return re.sub(r'\{[^}]+\}', r'[^/]+', path)
        return re.fullmatch(path_to_regex(path1), path2) or re.fullmatch(path_to_regex(path2), path1)
    
    def _convert_param_type(self, value: Any, param_type: Type) -> Any:
        if param_type == int:
            return int(value)
        elif param_type == float:
            return float(value)
        elif param_type == bool:
            return value.lower() in ('true', 'yes', '1')
        return value
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, **kwargs):
        import uvicorn
        uvicorn.run(self.app, host=host, port=port, **kwargs)