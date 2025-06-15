"""
MySQL 저장소 모듈

이 모듈은 MySQL 데이터베이스에 대한 저장소 구현을 제공합니다.
"""

import pymysql
from urllib.parse import urlparse
from typing import Dict, List, Optional, Any, Type, TypeVar, get_type_hints

from ezyapi.database.repositories.base import EzyRepository
from ezyapi.database.filters import (
    Not, LessThan, LessThanOrEqual, MoreThan, MoreThanOrEqual,
    Equal, Like, ILike, Between, In, IsNull
)
from ezyapi.utils.inflection import get_table_name_from_entity

T = TypeVar('T')

class MySQLRepository(EzyRepository[T]):
    """
    MySQL 데이터베이스를 위한 저장소 구현
    
    이 클래스는 EzyRepository 인터페이스를 구현하여 MySQL 데이터베이스에 
    데이터를 저장하고 접근하는 기능을 제공합니다.
    """
    
    def __init__(self, connection_string: str, entity_class: Type[T]):
        """
        MySQL 저장소 초기화
        
        Args:
            connection_string (str): MySQL 데이터베이스 연결 문자열
            entity_class (Type[T]): 이 저장소가 관리할 엔티티 클래스
        """
        self.connection_string = connection_string
        self.entity_class = entity_class
        self.table_name = get_table_name_from_entity(entity_class)
        self._ensure_table_exists()
        
    def _get_conn(self):
        """
        MySQL 데이터베이스 연결을 생성합니다.
        
        Returns:
            pymysql.Connection: 데이터베이스 연결 객체
        """
        parsed = urlparse(self.connection_string)
        conn = pymysql.connect(
            host=parsed.hostname,
            port=parsed.port if parsed.port else 3306,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path.lstrip("/")
        )
        return conn
    
    def _ensure_table_exists(self):
        """
        엔티티에 해당하는 테이블이 존재하는지 확인하고, 없으면 생성합니다.
        """
        from ezyapi.database.decorators import get_column_metadata
        
        entity_instance = self.entity_class()
        column_metadata = get_column_metadata(self.entity_class)
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
            
            meta = column_metadata.get(attr_name)
            if meta:
                if meta.column_type:
                    sql_type = meta.column_type
                
                if meta.primary:
                    if meta.auto_increment:
                        columns.append(f"{attr_name} {sql_type} AUTO_INCREMENT PRIMARY KEY")
                    else:
                        columns.append(f"{attr_name} {sql_type} PRIMARY KEY")
                else:
                    nullable = " NOT NULL" if not meta.nullable else ""
                    unique = " UNIQUE" if meta.unique else ""
                    columns.append(f"{attr_name} {sql_type}{nullable}{unique}")
            else:
                if attr_name == 'id':
                    columns.append(f"{attr_name} INT AUTO_INCREMENT PRIMARY KEY")
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
                where_parts.append(f"{key} LIKE %s")
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
        MySQL 결과 행을 엔티티 객체로 변환합니다.
        
        Args:
            row (dict): 데이터베이스 결과 행
            
        Returns:
            T: 변환된 엔티티 객체
        """
        entity = self.entity_class()
        for key, value in row.items():
            setattr(entity, key, value)
        return entity
    
    def _get_relation_metadata(self) -> Dict[str, Any]:
        """
        엔티티 클래스에서 관계 메타데이터를 추출합니다.
        
        Returns:
            Dict[str, Any]: 관계 필드명을 키로 하는 관계 메타데이터 딕셔너리
        """
        relations = {}
        
        for attr_name in dir(self.entity_class):
            if attr_name.startswith('_'):
                continue
            
            attr_value = getattr(self.entity_class, attr_name, None)
            if isinstance(attr_value, dict) and '_relation_type' in attr_value:
                relations[attr_name] = attr_value
        
        try:
            type_hints = get_type_hints(self.entity_class)
            for field_name, field_type in type_hints.items():
                if field_name.startswith('_'):
                    continue
                
                if hasattr(field_type, '__origin__') and field_type.__origin__ is list:
                    if hasattr(field_type, '__args__') and field_type.__args__:
                        target_entity = field_type.__args__[0]
                        if field_name not in relations:
                            relations[field_name] = {
                                '_relation_type': 'one_to_many',
                                '_target_entity': target_entity,
                                '_mapped_by': f"{self.table_name}_id"
                            }
        except Exception:
            pass
        
        return relations
    
    async def _load_relations(self, entities: List[T], relations_config: List[str]) -> List[T]:
        """
        엔티티 목록에 관계 데이터를 로드합니다.
        
        Args:
            entities: 관계를 로드할 엔티티 목록
            relations_config: 로드할 관계 설정
            
        Returns:
            List[T]: 관계 데이터가 로드된 엔티티 목록
        """
        if not entities or not relations_config:
            return entities
        
        if not isinstance(relations_config, list):
            raise ValueError("relations must be a list of relation names, e.g., ['card', 'posts']")
        
        relations_dict = {name: True for name in relations_config}
        relation_metadata = self._get_relation_metadata()
        
        for relation_name, relation_options in relations_dict.items():
            if relation_name not in relation_metadata:
                continue
            
            relation_info = relation_metadata[relation_name]
            relation_type = relation_info.get('_relation_type')
            target_entity = relation_info.get('_target_entity')
            
            if not target_entity:
                continue
            
            target_table = get_table_name_from_entity(target_entity)
            
            if relation_type == 'many_to_one':
                foreign_key = relation_info.get('_foreign_key', f"{relation_name}_id")
                await self._load_many_to_one_relation(entities, relation_name, target_entity, target_table, foreign_key)
                
            elif relation_type == 'one_to_many':
                mapped_by = relation_info.get('_mapped_by', f"{self.table_name}_id")
                await self._load_one_to_many_relation(entities, relation_name, target_entity, target_table, mapped_by)
        
        return entities
    
    async def _load_many_to_one_relation(self, entities: List[T], relation_name: str, 
                                       target_entity: Type, target_table: str, foreign_key: str):
        """
        ManyToOne 관계 데이터를 로드합니다.
        """
        foreign_key_values = []
        for entity in entities:
            fk_value = getattr(entity, foreign_key, None)
            if fk_value is not None:
                foreign_key_values.append(fk_value)
        
        if not foreign_key_values:
            return
        
        unique_fk_values = list(set(foreign_key_values))
        
        placeholders = ', '.join('%s' for _ in unique_fk_values)
        query = f'SELECT * FROM {target_table} WHERE id IN ({placeholders})'
        
        conn = self._get_conn()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, unique_fk_values)
        related_rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        related_entities = {}
        for row in related_rows:
            related_entity = target_entity()
            for key, value in row.items():
                setattr(related_entity, key, value)
            related_entities[row['id']] = related_entity
        
        for entity in entities:
            fk_value = getattr(entity, foreign_key, None)
            if fk_value in related_entities:
                setattr(entity, relation_name, related_entities[fk_value])
    
    async def _load_one_to_many_relation(self, entities: List[T], relation_name: str,
                                       target_entity: Type, target_table: str, mapped_by: str):
        """
        OneToMany 관계 데이터를 로드합니다.
        """
        parent_ids = []
        for entity in entities:
            parent_id = getattr(entity, 'id', None)
            if parent_id is not None:
                parent_ids.append(parent_id)
        
        if not parent_ids:
            return
        
        unique_parent_ids = list(set(parent_ids))
        
        placeholders = ', '.join('%s' for _ in unique_parent_ids)
        query = f'SELECT * FROM {target_table} WHERE {mapped_by} IN ({placeholders})'
        
        conn = self._get_conn()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, unique_parent_ids)
        related_rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        children_by_parent = {}
        for row in related_rows:
            related_entity = target_entity()
            for key, value in row.items():
                setattr(related_entity, key, value)
            
            parent_id = row[mapped_by]
            if parent_id not in children_by_parent:
                children_by_parent[parent_id] = []
            children_by_parent[parent_id].append(related_entity)
        
        for entity in entities:
            parent_id = getattr(entity, 'id', None)
            if parent_id in children_by_parent:
                setattr(entity, relation_name, children_by_parent[parent_id])
            else:
                setattr(entity, relation_name, [])
    
    async def find(self, 
                  where: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None, 
                  select: Optional[List[str]] = None, 
                  relations: Optional[List[str]] = None, 
                  order: Optional[Dict[str, str]] = None, 
                  skip: Optional[int] = None, 
                  take: Optional[int] = None) -> List[T]:
        """
        조건에 맞는 엔티티 목록을 검색합니다.
        
        Args:
            where: 검색 조건
            select: 선택할 필드 목록
            relations: 함께 로드할 관계 데이터. 예: ["user", "posts"]
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
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, values)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        entities = [self._row_to_entity(row) for row in rows]
        
        if relations:
            entities = await self._load_relations(entities, relations)
        
        return entities
    
    async def find_one(self, 
                      where: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None, 
                      select: Optional[List[str]] = None, 
                      relations: Optional[List[str]] = None) -> Optional[T]:
        """
        조건에 맞는 단일 엔티티를 검색합니다.
        
        Args:
            where: 검색 조건
            select: 선택할 필드 목록
            relations: 함께 로드할 관계 데이터. 예: {"user": True, "posts": {"select": ["title", "content"]}}
            
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
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, values)
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row:
            return None
        
        entity = self._row_to_entity(row)
        
        if relations:
            entities = await self._load_relations([entity], relations)
            return entities[0] if entities else entity
        
        return entity
    
    async def save(self, entity: T) -> T:
        """
        엔티티를 저장합니다. primary key가 없으면 생성하고, 있으면 업데이트합니다.
        
        Args:
            entity: 저장할 엔티티 인스턴스
            
        Returns:
            T: 저장된 엔티티
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        attrs = {k: v for k, v in entity.__dict__.items() if not k.startswith('_')}
        
        pk_info = entity.get_primary_key_info()
        pk_field = pk_info['field_name']
        pk_auto_increment = pk_info['auto_increment']
        
        pk_value = getattr(entity, pk_field, None)
        
        try:
            if pk_auto_increment and pk_value is None:
                columns = ', '.join(k for k in attrs.keys() if k != pk_field)
                placeholders = ', '.join('%s' for _ in range(len(attrs) - (1 if pk_field in attrs else 0)))
                values = [v for k, v in attrs.items() if k != pk_field]
                
                query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders});"
                cursor.execute(query, values)
                entity.id = cursor.lastrowid
            elif not pk_auto_increment and pk_value is None:
                raise ValueError(f"Primary key '{pk_field}' 값이 필요합니다.")
            elif pk_value is not None:
                check_query = f"SELECT COUNT(*) FROM {self.table_name} WHERE {pk_field} = %s;"
                cursor.execute(check_query, (pk_value,))
                exists = cursor.fetchone()[0] > 0
                
                if exists:
                    set_clause = ', '.join(f"{k} = %s" for k in attrs.keys() if k != pk_field)
                    values = [v for k, v in attrs.items() if k != pk_field]
                    values.append(pk_value)
                    
                    query = f"UPDATE {self.table_name} SET {set_clause} WHERE {pk_field} = %s;"
                    cursor.execute(query, values)
                else:
                    columns = ', '.join(attrs.keys())
                    placeholders = ', '.join('%s' for _ in range(len(attrs)))
                    values = list(attrs.values())
                    
                    query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders});"
                    cursor.execute(query, values)
            
            conn.commit()
        finally:
            cursor.close()
            conn.close()
        
        return entity
    
    async def delete(self, id: Any) -> bool:
        """
        지정된 Primary Key의 엔티티를 삭제합니다.
        
        Args:
            id: 삭제할 엔티티의 Primary Key 값
            
        Returns:
            bool: 삭제 성공 여부
        """
        entity_instance = self.entity_class()
        pk_info = entity_instance.get_primary_key_info()
        pk_field = pk_info['field_name']
        
        conn = self._get_conn()
        cursor = conn.cursor()
        query = f"DELETE FROM {self.table_name} WHERE {pk_field} = %s;"
        cursor.execute(query, (id,))
        conn.commit()
        rowcount = cursor.rowcount
        cursor.close()
        conn.close()
        
        return rowcount > 0