"""
데이터베이스 설정 모듈

이 모듈은 데이터베이스 연결과 저장소를 설정하는 클래스를 제공합니다.
"""

import sys
from typing import Dict, Type, TypeVar

from ezyapi.database.entity import EzyEntityBase
from ezyapi.database.repositories.base import EzyRepository
from ezyapi.database.repositories.sqlite import SQLiteRepository
from ezyapi.database.repositories.postgres import PostgreSQLRepository
from ezyapi.database.repositories.mongodb import MongoDBRepository
from ezyapi.database.repositories.mysql import MySQLRepository

T = TypeVar('T')

class DatabaseConfig:
    """
    데이터베이스 연결 및 저장소를 설정하는 클래스
    
    이 클래스는 다양한 데이터베이스 유형(SQLite, PostgreSQL, MySQL, MongoDB 등)에 
    대한 연결을 설정하고 적절한 저장소를 생성할 수 있도록 합니다.
    """
    
    def __init__(self, db_type: str = "sqlite", connection_string: str = None, connection_params: dict = None):
        """
        데이터베이스 설정 초기화
        
        Args:
            db_type (str): 데이터베이스 유형 ("sqlite", "postgresql", "mysql", "mongodb")
            connection_string (str, optional): 데이터베이스 연결 문자열
            connection_params (dict, optional): 데이터베이스 연결 매개변수
        
        Raises:
            ValueError: 연결 문자열이나 연결 매개변수가 제공되지 않은 경우
        """
        self.db_type = db_type
        self.connection_string = connection_string
        self.connection_params = connection_params or {}
        
        if not connection_string and not connection_params:
            if db_type == "sqlite":
                self.connection_string = ":memory:"
            else:
                raise ValueError(f"{db_type} 데이터베이스에는 connection_string 또는 connection_params가 필요합니다.")
        
        self._session_factory = None
    
    def get_connection_string(self) -> str:
        """
        데이터베이스 연결 문자열을 반환합니다.
        
        연결 문자열이 직접 제공된 경우 그대로 반환하고,
        연결 매개변수가 제공된 경우 데이터베이스 유형에 맞는 연결 문자열을 생성합니다.
        
        Returns:
            str: 데이터베이스 연결 문자열
            
        Raises:
            ValueError: 지원되지 않는 데이터베이스 유형이 지정된 경우
        """
        if self.connection_string:
            return self.connection_string
            
        if self.db_type == "sqlite":
            return self.connection_params.get("dbname", ":memory:")
        elif self.db_type == "postgresql":
            return f"postgresql://{self.connection_params.get('user', '')}:{self.connection_params.get('password', '')}@{self.connection_params.get('host', 'localhost')}:{self.connection_params.get('port', 5432)}/{self.connection_params.get('dbname', '')}"
        elif self.db_type == "mysql":
            return f"mysql://{self.connection_params.get('user', '')}:{self.connection_params.get('password', '')}@{self.connection_params.get('host', 'localhost')}:{self.connection_params.get('port', 3306)}/{self.connection_params.get('dbname', '')}"
        elif self.db_type == "mongodb":
            auth = f"{self.connection_params.get('user', '')}:{self.connection_params.get('password', '')}@" if self.connection_params.get('user') else ""
            return f"mongodb://{auth}{self.connection_params.get('host', 'localhost')}:{self.connection_params.get('port', 27017)}/{self.connection_params.get('dbname', '')}"
        else:
            raise ValueError(f"지원되지 않는 데이터베이스 유형입니다: {self.db_type}")
    
    def get_repository(self, entity_class: Type[T]) -> EzyRepository[T]:
        """
        지정된 엔티티 클래스에 대한 저장소를 생성합니다.
        
        Args:
            entity_class (Type[T]): 엔티티 클래스
            
        Returns:
            EzyRepository[T]: 엔티티를 관리하는 저장소 인스턴스
            
        Raises:
            ValueError: 지원되지 않는 데이터베이스 유형이 지정된 경우
        """
        conn_str = self.get_connection_string()
        
        if self.db_type == "sqlite":
            return SQLiteRepository(conn_str, entity_class)
        elif self.db_type == "postgresql":
            return PostgreSQLRepository(conn_str, entity_class)
        elif self.db_type == "mongodb":
            return MongoDBRepository(conn_str, entity_class)
        elif self.db_type == "mysql":
            return MySQLRepository(conn_str, entity_class)
        else:
            raise ValueError(f"지원되지 않는 데이터베이스 유형입니다: {self.db_type}")


def auto_inject_repository(service_class, db_config: DatabaseConfig):
    """
    서비스 클래스 이름을 기반으로 자동으로 엔티티를 찾아 저장소를 주입합니다.
    
    Args:
        service_class: 서비스 클래스
        db_config (DatabaseConfig): 데이터베이스 설정 객체
        
    Returns:
        서비스 인스턴스(저장소가 주입됨)
    """
    service_name = service_class.__name__
    entity_class_name = None
    
    if service_name.endswith("Service"):
        entity_name = service_name[:-7]
        entity_class_name = f"{entity_name}Entity"
        
    entity_class = None
    
    for module_name, module in sys.modules.items():
        if hasattr(module, entity_class_name):
            entity_class = getattr(module, entity_class_name)
            break
            
    if entity_class and issubclass(entity_class, EzyEntityBase):
        repository = db_config.get_repository(entity_class)
        return service_class(repository=repository)
        
    return service_class()