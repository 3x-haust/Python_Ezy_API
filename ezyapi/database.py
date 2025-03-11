
from abc import ABC, abstractmethod
from typing import Type, List, Optional, Generic, TypeVar

T = TypeVar('T')

class EzyRepository(Generic[T], ABC):
    """
    데이터 저장소 추상 인터페이스
    다양한 ORM 또는 데이터베이스 구현을 위한 기본 클래스
    """
    @abstractmethod
    async def find_by_id(self, id: int) -> Optional[T]:
        """ID로 엔티티 조회"""
        pass
    
    @abstractmethod
    async def find_all(self) -> List[T]:
        """모든 엔티티 조회"""
        pass
    
    @abstractmethod
    async def save(self, entity: T) -> T:
        """엔티티 저장 (생성 또는 업데이트)"""
        pass
    
    @abstractmethod
    async def delete(self, id: int) -> bool:
        """엔티티 삭제"""
        pass


class SQLiteRepository(EzyRepository[T]):
    """
    SQLite 기반 저장소 구현
    직접 SQL 쿼리를 사용하여 엔티티를 관리
    """
    def __init__(self, db_path: str, entity_class: Type[T]):
        import sqlite3
        self.db_path = db_path
        self.entity_class = entity_class
        self.table_name = self._get_table_name(entity_class)
        self._ensure_table_exists()
    
    def _get_table_name(self, entity_class: Type[T]) -> str:
        import inflect
        p = inflect.engine()
        name = entity_class.__name__
        if name.endswith("Entity"):
            name = name[:-6]
        return p.plural(name.lower())
    
    def _get_conn(self):
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _ensure_table_exists(self):
        entity_instance = self.entity_class()
        columns = []
        
        for attr_name, attr_value in entity_instance.__dict__.items():
            if attr_name.startswith('_'):
                continue
            
            attr_type = type(attr_value) if attr_value is not None else str
            sql_type = "TEXT" 
            
            if attr_type == int:
                sql_type = "INTEGER"
            elif attr_type == float:
                sql_type = "REAL"
            elif attr_type == bool:
                sql_type = "INTEGER"

            if attr_name == 'id':
                columns.append(f"{attr_name} INTEGER PRIMARY KEY AUTOINCREMENT")
            else:
                columns.append(f"{attr_name} {sql_type}")
        
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name} (
            {', '.join(columns)}
        );
        """
        
        with self._get_conn() as conn:
            conn.execute(create_table_sql)
    
    async def find_by_id(self, id: int) -> Optional[T]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            query = f"SELECT * FROM {self.table_name} WHERE id = ?;"
            cursor.execute(query, (id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            return self._row_to_entity(row)
    
    async def find_all(self) -> List[T]:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            query = f"SELECT * FROM {self.table_name};"
            cursor.execute(query)
            rows = cursor.fetchall()
            
            return [self._row_to_entity(row) for row in rows]
    
    async def save(self, entity: T) -> T:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            attrs = {k: v for k, v in entity.__dict__.items() if not k.startswith('_')}
            
            if getattr(entity, 'id', None) is None:
                columns = ', '.join(k for k in attrs.keys() if k != 'id')
                placeholders = ', '.join('?' for _ in range(len(attrs) - (1 if 'id' in attrs else 0)))
                values = [v for k, v in attrs.items() if k != 'id']
                
                query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders});"
                cursor.execute(query, values)
                
                setattr(entity, 'id', cursor.lastrowid)
            else:
                set_clause = ', '.join(f"{k} = ?" for k in attrs.keys() if k != 'id')
                values = [v for k, v in attrs.items() if k != 'id']
                values.append(attrs.get('id'))
                
                query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = ?;"
                cursor.execute(query, values)
            
            return entity
    
    async def delete(self, id: int) -> bool:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            query = f"DELETE FROM {self.table_name} WHERE id = ?;"
            cursor.execute(query, (id,))
            return cursor.rowcount > 0
    
    def _row_to_entity(self, row) -> T:
        import sqlite3
        entity = self.entity_class()
        for key in row.keys():
            setattr(entity, key, row[key])
        return entity

class EzyEntityBase:
    id: int = None


class EzyService:
    def __init__(self, repository: Optional[EzyRepository] = None):
        self.repository = repository


class DatabaseConfig:
    def __init__(self, db_type: str = "sqlite", connection_string: str = ":memory:"):
        self.db_type = db_type
        self.connection_string = connection_string
        self._session_factory = None
    
    def get_repository(self, entity_class: Type[T]) -> EzyRepository[T]:
        if self.db_type == "sqlite":
            return SQLiteRepository(self.connection_string, entity_class)
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")


def auto_inject_repository(service_class: Type[EzyService], db_config: DatabaseConfig):
    service_name = service_class.__name__
    entity_class_name = None
    
    if service_name.endswith("Service"):
        entity_name = service_name[:-7]
        entity_class_name = f"{entity_name}Entity"
    
    import sys
    entity_class = None
    for module_name, module in sys.modules.items():
        if hasattr(module, entity_class_name):
            entity_class = getattr(module, entity_class_name)
            break
    
    if entity_class and issubclass(entity_class, EzyEntityBase):
        repository = db_config.get_repository(entity_class)
        return service_class(repository=repository)
    
    return service_class()