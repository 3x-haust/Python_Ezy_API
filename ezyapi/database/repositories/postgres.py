"""
PostgreSQL 저장소 모듈

이 모듈은 PostgreSQL 데이터베이스에 대한 저장소 구현을 제공합니다.
"""

import psycopg2
import psycopg2.extras
from typing import Dict, List, Optional, Any, Type, TypeVar

from ezyapi.database.repositories.base import EzyRepository
from ezyapi.database.filters import (
    Not, LessThan, LessThanOrEqual, MoreThan, MoreThanOrEqual,
    Equal, Like, ILike, Between, In, IsNull
)
from ezyapi.utils.inflection import get_table_name_from_entity

T = TypeVar('T')

class PostgreSQLRepository(EzyRepository[T]):
    """
    PostgreSQL 데이터베이스를 위한 저장소 구현
    
    이 클래스는 EzyRepository 인터페이스를 구현하여 PostgreSQL 데이터베이스에 
    데이터를 저장하고 접근하는 기능을 제공합니다.
    """
    
    def __init__(self, connection_string: str, entity_class: Type[T]):
        """
        PostgreSQL 저장소 초기화
        
        Args:
            connection_string (str): PostgreSQL 데이터베이스 연결 문자열
            entity_class (Type[T]): 이 저장소가 관리할 엔티티 클래스
        """
        self.connection_string = connection_string
        self.entity_class = entity_class
        self.table_name = get_table_name_from_entity(entity_class)
        self._ensure_table_exists()
        
    def _get_conn(self):
        """
        PostgreSQL 데이터베이스 연결을 생성합니다.
        
        Returns:
            psycopg2.connection: 데이터베이스 연결 객체
        """
        conn = psycopg2.connect(self.connection_string)
        return conn
    
    def _ensure_table_exists(self):
        """
        엔티티에 해당하는 테이블이 존재하는지 확인하고, 없으면 생성합니다.
        """
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
                sql_type = "BOOLEAN"
                
            if attr_name == 'id':
                columns.append(f"{attr_name} SERIAL PRIMARY KEY")
            else:
                columns.append(f"{attr_name} {sql_type}")
                
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {self.table_name} ({', '.join(columns)});"
        
        conn = self._get_conn()
        cursor = conn.cursor()
        cursor.execute(create_table_sql)
        conn.commit()
        cursor.close()
        conn.close()
    
    def _build_where_clause(self, conditions: Dict[str, Any]) -> tuple[List[str], List[Any]]:
        """
        조건 딕셔너리에서 SQL WHERE 절을 구성합니다.
        
        Args:
            conditions (Dict[str, Any]): 검색 조건
            
        Returns:
            tuple[List[str], List[Any]]: WHERE 절의 조건 부분과 파라미터 값 목록
        """
        where_parts = []
        values = []
        
        for key, value in conditions.items():
            if isinstance(value, Not):
                where_parts.append(f"{key} != %s")
                values.append(value.value)
            elif isinstance(value, LessThan):
                where_parts.append(f"{key} < %s")
                values.append(value.value)
            elif isinstance(value, LessThanOrEqual):
                where_parts.append(f"{key} <= %s")
                values.append(value.value)
            elif isinstance(value, MoreThan):
                where_parts.append(f"{key} > %s")
                values.append(value.value)
            elif isinstance(value, MoreThanOrEqual):
                where_parts.append(f"{key} >= %s")
                values.append(value.value)
            elif isinstance(value, Equal):
                where_parts.append(f"{key} = %s")
                values.append(value.value)
            elif isinstance(value, Like):
                where_parts.append(f"{key} LIKE %s")
                values.append(value.value)
            elif isinstance(value, ILike):
                where_parts.append(f"{key} ILIKE %s")
                values.append(value.value)
            elif isinstance(value, Between):
                where_parts.append(f"{key} BETWEEN %s AND %s")
                values.extend([value.min, value.max])
            elif isinstance(value, In):
                placeholders = ', '.join('%s' for _ in value.values)
                where_parts.append(f"{key} IN ({placeholders})")
                values.extend(value.values)
            elif isinstance(value, IsNull):
                where_parts.append(f"{key} IS NULL")
            else:
                where_parts.append(f"{key} = %s")
                values.append(value)
                
        return where_parts, values
    
    def _row_to_entity(self, row) -> T:
        """
        PostgreSQL 결과 행을 엔티티 객체로 변환합니다.
        
        Args:
            row (dict): 데이터베이스 결과 행
            
        Returns:
            T: 변환된 엔티티 객체
        """
        entity = self.entity_class()
        for key in row.keys():
            setattr(entity, key, row[key])
        return entity
    
    async def find(self, 
                  where: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None, 
                  select: Optional[List[str]] = None, 
                  relations: Optional[Dict[str, Any]] = None, 
                  order: Optional[Dict[str, str]] = None, 
                  skip: Optional[int] = None, 
                  take: Optional[int] = None) -> List[T]:
        """
        조건에 맞는 엔티티 목록을 검색합니다.
        
        Args:
            where: 검색 조건
            select: 선택할 필드 목록
            relations: 함께 로드할 관계 데이터 (PostgreSQL에서는 구현되지 않음)
            order: 정렬 조건
            skip: 건너뛸 결과 수
            take: 가져올 결과 수
            
        Returns:
            List[T]: 검색된 엔티티 목록
        """
        fields = ', '.join(select) if select else '*'
        query = f"SELECT {fields} FROM {self.table_name}"
        values = []
        
        if where:
            if isinstance(where, list):
                or_conditions = []
                for cond in where:
                    parts, vals = self._build_where_clause(cond)
                    or_conditions.append(f"({' AND '.join(parts)})")
                    values.extend(vals)
                query += f" WHERE {' OR '.join(or_conditions)}"
            else:
                where_parts, vals = self._build_where_clause(where)
                query += f" WHERE {' AND '.join(where_parts)}"
                values.extend(vals)
                
        if order:
            order_clause = ', '.join(f"{k} {v}" for k, v in order.items())
            query += f" ORDER BY {order_clause}"
            
        if skip is not None and take is not None:
            query += f" LIMIT {take} OFFSET {skip}"
        elif take is not None:
            query += f" LIMIT {take}"
        elif skip is not None:
            query += f" OFFSET {skip}"
            
        conn = self._get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(query, values)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return [self._row_to_entity(row) for row in rows]
    
    async def find_one(self, 
                      where: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None, 
                      select: Optional[List[str]] = None, 
                      relations: Optional[Dict[str, Any]] = None) -> Optional[T]:
        """
        조건에 맞는 단일 엔티티를 검색합니다.
        
        Args:
            where: 검색 조건
            select: 선택할 필드 목록
            relations: 함께 로드할 관계 데이터 (PostgreSQL에서는 구현되지 않음)
            
        Returns:
            Optional[T]: 검색된 엔티티 또는 None
        """
        fields = ', '.join(select) if select else '*'
        query = f"SELECT {fields} FROM {self.table_name}"
        values = []
        
        if where:
            if isinstance(where, list):
                or_conditions = []
                for cond in where:
                    parts, vals = self._build_where_clause(cond)
                    or_conditions.append(f"({' AND '.join(parts)})")
                    values.extend(vals)
                query += f" WHERE {' OR '.join(or_conditions)}"
            else:
                where_parts, vals = self._build_where_clause(where)
                query += f" WHERE {' AND '.join(where_parts)}"
                values.extend(vals)
                
        query += " LIMIT 1"
        
        conn = self._get_conn()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(query, values)
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return self._row_to_entity(row) if row else None
    
    async def save(self, entity: T) -> T:
        """
        엔티티를 저장합니다. id가 없으면 생성하고, 있으면 업데이트합니다.
        
        Args:
            entity: 저장할 엔티티 인스턴스
            
        Returns:
            T: 저장된 엔티티
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        attrs = {k: v for k, v in entity.__dict__.items() if not k.startswith('_')}
        
        if getattr(entity, 'id', None) is None:
            columns = ', '.join(k for k in attrs.keys() if k != 'id')
            placeholders = ', '.join('%s' for _ in range(len(attrs) - (1 if 'id' in attrs else 0)))
            values = [v for k, v in attrs.items() if k != 'id']
            
            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders}) RETURNING id;"
            cursor.execute(query, values)
            entity.id = cursor.fetchone()[0]
        else:
            set_clause = ', '.join(f"{k} = %s" for k in attrs.keys() if k != 'id')
            values = [v for k, v in attrs.items() if k != 'id']
            values.append(attrs.get('id'))
            
            query = f"UPDATE {self.table_name} SET {set_clause} WHERE id = %s;"
            cursor.execute(query, values)
            
        conn.commit()
        cursor.close()
        conn.close()
        
        return entity
    
    async def delete(self, id: int) -> bool:
        """
        지정된 ID의 엔티티를 삭제합니다.
        
        Args:
            id: 삭제할 엔티티의 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        query = f"DELETE FROM {self.table_name} WHERE id = %s;"
        cursor.execute(query, (id,))
        conn.commit()
        rowcount = cursor.rowcount
        cursor.close()
        conn.close()
        
        return rowcount > 0