"""
SQLite 저장소 모듈

이 모듈은 SQLite 데이터베이스에 대한 저장소 구현을 제공합니다.
"""

import sqlite3
from typing import Dict, List, Optional, Any, Type, TypeVar, get_type_hints

from ezyapi.database.repositories.base import EzyRepository
from ezyapi.database.filters import (
    Not, LessThan, LessThanOrEqual, MoreThan, MoreThanOrEqual,
    Equal, Like, ILike, Between, In, IsNull
)
from ezyapi.utils.inflection import get_table_name_from_entity

T = TypeVar('T')

class SQLiteRepository(EzyRepository[T]):
    """
    SQLite 데이터베이스를 위한 저장소 구현
    
    이 클래스는 EzyRepository 인터페이스를 구현하여 SQLite 데이터베이스에 
    데이터를 저장하고 접근하는 기능을 제공합니다.
    """
    
    def __init__(self, db_path: str, entity_class: Type[T]):
        """
        SQLite 저장소 초기화
        
        Args:
            db_path (str): SQLite 데이터베이스 파일 경로
            entity_class (Type[T]): 이 저장소가 관리할 엔티티 클래스
        """
        self.db_path = db_path
        self.entity_class = entity_class
        self.table_name = get_table_name_from_entity(entity_class)
        self._ensure_table_exists()
        
    def _get_conn(self):
        """
        SQLite 데이터베이스 연결을 생성합니다.
        
        Returns:
            sqlite3.Connection: 데이터베이스 연결 객체
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
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
                sql_type = "INTEGER"
            
            meta = column_metadata.get(attr_name)
            if meta:
                if meta.column_type:
                    sql_type = meta.column_type
                
                if meta.primary:
                    if meta.auto_increment:
                        columns.append(f"{attr_name} {sql_type} PRIMARY KEY AUTOINCREMENT")
                    else:
                        columns.append(f"{attr_name} {sql_type} PRIMARY KEY")
                else:
                    nullable = " NOT NULL" if not meta.nullable else ""
                    unique = " UNIQUE" if meta.unique else ""
                    columns.append(f"{attr_name} {sql_type}{nullable}{unique}")
            else:
                if attr_name == 'id':
                    columns.append(f"{attr_name} INTEGER PRIMARY KEY AUTOINCREMENT")
                else:
                    columns.append(f"{attr_name} {sql_type}")
                
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {self.table_name} ({', '.join(columns)});"
        
        with self._get_conn() as conn:
            conn.execute(create_table_sql)
    
    def _get_relation_metadata(self):
        """
        엔티티 클래스에서 관계 메타데이터를 추출합니다.
        
        Returns:
            Dict[str, Any]: 관계 메타데이터
        """
        from ezyapi.database.decorators import OneToMany, ManyToOne
        
        relations = {}
        type_hints = get_type_hints(self.entity_class)
        
        for attr_name, attr_value in self.entity_class.__dict__.items():
            if isinstance(attr_value, (OneToMany, ManyToOne)):
                relations[attr_name] = {
                    'type': 'one_to_many' if isinstance(attr_value, OneToMany) else 'many_to_one',
                    'target_entity': attr_value.target_entity,
                    'foreign_key': attr_value.foreign_key,
                    'metadata': attr_value
                }
                
        return relations
    
    def _load_relations(self, entities: List[T], relations: List[str]) -> List[T]:
        """
        엔티티 목록에 대해 관계 데이터를 로드합니다.
        
        Args:
            entities: 관계를 로드할 엔티티 목록
            relations: 로드할 관계 이름 목록
            
        Returns:
            List[T]: 관계가 로드된 엔티티 목록
        """
        if not entities or not relations:
            return entities
            
        relation_metadata = self._get_relation_metadata()
        
        for relation_name in relations:
            if relation_name not in relation_metadata:
                continue
                
            rel_meta = relation_metadata[relation_name]
            if rel_meta['type'] == 'many_to_one':
                entities = self._load_many_to_one_relation(entities, relation_name, rel_meta)
            elif rel_meta['type'] == 'one_to_many':
                entities = self._load_one_to_many_relation(entities, relation_name, rel_meta)
                
        return entities
    
    def _load_many_to_one_relation(self, entities: List[T], relation_name: str, rel_meta: Dict[str, Any]) -> List[T]:
        """
        ManyToOne 관계 데이터를 로드합니다.
        
        Args:
            entities: 엔티티 목록
            relation_name: 관계 이름
            rel_meta: 관계 메타데이터
            
        Returns:
            List[T]: 관계가 로드된 엔티티 목록
        """
        target_entity = rel_meta['target_entity']
        foreign_key = rel_meta['foreign_key']
        
        foreign_key_values = set()
        for entity in entities:
            fk_value = getattr(entity, foreign_key, None)
            if fk_value is not None:
                foreign_key_values.add(fk_value)
        
        if not foreign_key_values:
            return entities
            
        from ezyapi.utils.inflection import get_table_name_from_entity
        target_table = get_table_name_from_entity(target_entity)
        target_pk_info = target_entity().get_primary_key_info()
        target_pk_field = target_pk_info['field_name']
        
        placeholders = ', '.join('?' for _ in foreign_key_values)
        query = f"SELECT * FROM {target_table} WHERE {target_pk_field} IN ({placeholders})"
        
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(query, list(foreign_key_values))
            rows = cursor.fetchall()
            
            related_entities = {}
            for row in rows:
                related_entity = target_entity()
                for key in row.keys():
                    setattr(related_entity, key, row[key])
                related_entities[getattr(related_entity, target_pk_field)] = related_entity
        
        for entity in entities:
            fk_value = getattr(entity, foreign_key, None)
            if fk_value in related_entities:
                setattr(entity, relation_name, related_entities[fk_value])
            else:
                setattr(entity, relation_name, None)
                
        return entities
    
    def _load_one_to_many_relation(self, entities: List[T], relation_name: str, rel_meta: Dict[str, Any]) -> List[T]:
        """
        OneToMany 관계 데이터를 로드합니다.
        
        Args:
            entities: 엔티티 목록
            relation_name: 관계 이름
            rel_meta: 관계 메타데이터
            
        Returns:
            List[T]: 관계가 로드된 엔티티 목록
        """
        target_entity = rel_meta['target_entity']
        foreign_key = rel_meta['foreign_key']
        
        entity_pk_info = self.entity_class().get_primary_key_info()
        entity_pk_field = entity_pk_info['field_name']
        
        primary_key_values = set()
        for entity in entities:
            pk_value = getattr(entity, entity_pk_field, None)
            if pk_value is not None:
                primary_key_values.add(pk_value)
        
        if not primary_key_values:
            return entities
            
        from ezyapi.utils.inflection import get_table_name_from_entity
        target_table = get_table_name_from_entity(target_entity)
        
        placeholders = ', '.join('?' for _ in primary_key_values)
        query = f"SELECT * FROM {target_table} WHERE {foreign_key} IN ({placeholders})"
        
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(query, list(primary_key_values))
            rows = cursor.fetchall()
            
            related_entities_by_fk = {}
            for row in rows:
                related_entity = target_entity()
                for key in row.keys():
                    setattr(related_entity, key, row[key])
                
                fk_value = getattr(related_entity, foreign_key)
                if fk_value not in related_entities_by_fk:
                    related_entities_by_fk[fk_value] = []
                related_entities_by_fk[fk_value].append(related_entity)
        
        for entity in entities:
            pk_value = getattr(entity, entity_pk_field)
            setattr(entity, relation_name, related_entities_by_fk.get(pk_value, []))
                
        return entities
    
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
                where_parts.append(f"{key} != ?")
                values.append(value.value)
            elif isinstance(value, LessThan):
                where_parts.append(f"{key} < ?")
                values.append(value.value)
            elif isinstance(value, LessThanOrEqual):
                where_parts.append(f"{key} <= ?")
                values.append(value.value)
            elif isinstance(value, MoreThan):
                where_parts.append(f"{key} > ?")
                values.append(value.value)
            elif isinstance(value, MoreThanOrEqual):
                where_parts.append(f"{key} >= ?")
                values.append(value.value)
            elif isinstance(value, Equal):
                where_parts.append(f"{key} = ?")
                values.append(value.value)
            elif isinstance(value, Like):
                where_parts.append(f"{key} LIKE ?")
                values.append(value.value)
            elif isinstance(value, ILike):
                where_parts.append(f"{key} LIKE ?")
                values.append(value.value)
            elif isinstance(value, Between):
                where_parts.append(f"{key} BETWEEN ? AND ?")
                values.extend([value.min, value.max])
            elif isinstance(value, In):
                placeholders = ', '.join('?' for _ in value.values)
                where_parts.append(f"{key} IN ({placeholders})")
                values.extend(value.values)
            elif isinstance(value, IsNull):
                where_parts.append(f"{key} IS NULL")
            else:
                where_parts.append(f"{key} = ?")
                values.append(value)
                
        return where_parts, values
    
    def _row_to_entity(self, row) -> T:
        """
        SQLite 결과 행을 엔티티 객체로 변환합니다.
        
        Args:
            row (sqlite3.Row): 데이터베이스 결과 행
            
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
                  relations: Optional[List[str]] = None, 
                  order: Optional[Dict[str, str]] = None, 
                  skip: Optional[int] = None, 
                  take: Optional[int] = None) -> List[T]:
        """
        조건에 맞는 엔티티 목록을 검색합니다.
        
        Args:
            where: 검색 조건
            select: 선택할 필드 목록
            relations: 함께 로드할 관계 데이터
            order: 정렬 조건
            skip: 건너뛸 결과 수
            take: 가져올 결과 수
            
        Returns:
            List[T]: 검색된 엔티티 목록
        """
        if relations is not None and not isinstance(relations, list):
            raise ValueError(
                "relations 파라미터는 리스트 형태만 지원됩니다. "
                "예: relations=['posts'] (올바름), relations={'posts': True} (잘못됨)"
            )
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
            
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            rows = cursor.fetchall()
            entities = [self._row_to_entity(row) for row in rows]
            
            if relations:
                entities = self._load_relations(entities, relations)
                
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
            relations: 함께 로드할 관계 데이터
            
        Returns:
            Optional[T]: 검색된 엔티티 또는 None
        """
        if relations is not None and not isinstance(relations, list):
            raise ValueError(
                "relations 파라미터는 리스트 형태만 지원됩니다. "
                "예: relations=['posts'] (올바름), relations={'posts': True} (잘못됨)"
            )
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
        
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            row = cursor.fetchone()
            
            if row is None:
                return None
                
            entity = self._row_to_entity(row)
            
            if relations:
                entities = self._load_relations([entity], relations)
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
        with self._get_conn() as conn:
            cursor = conn.cursor()
            attrs = {k: v for k, v in entity.__dict__.items() if not k.startswith('_')}
            
            pk_info = entity.get_primary_key_info()
            pk_field = pk_info['field_name']
            pk_auto_increment = pk_info['auto_increment']
            
            pk_value = getattr(entity, pk_field, None)
            
            if pk_auto_increment and pk_value is None:
                columns = ', '.join(k for k in attrs.keys() if k != pk_field)
                placeholders = ', '.join('?' for _ in range(len(attrs) - (1 if pk_field in attrs else 0)))
                values = [v for k, v in attrs.items() if k != pk_field]
                
                query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders});"
                cursor.execute(query, values)
                setattr(entity, pk_field, cursor.lastrowid)
            elif not pk_auto_increment and pk_value is None:
                raise ValueError(f"Primary key '{pk_field}' 값이 필요합니다.")
            elif pk_value is not None:
                check_query = f"SELECT COUNT(*) FROM {self.table_name} WHERE {pk_field} = ?;"
                cursor.execute(check_query, (pk_value,))
                exists = cursor.fetchone()[0] > 0
                
                if exists:
                    set_clause = ', '.join(f"{k} = ?" for k in attrs.keys() if k != pk_field)
                    values = [v for k, v in attrs.items() if k != pk_field]
                    values.append(pk_value)
                    
                    query = f"UPDATE {self.table_name} SET {set_clause} WHERE {pk_field} = ?;"
                    cursor.execute(query, values)
                else:
                    columns = ', '.join(attrs.keys())
                    placeholders = ', '.join('?' for _ in range(len(attrs)))
                    values = list(attrs.values())
                    
                    query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders});"
                    cursor.execute(query, values)
                
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
        
        with self._get_conn() as conn:
            cursor = conn.cursor()
            query = f"DELETE FROM {self.table_name} WHERE {pk_field} = ?;"
            cursor.execute(query, (id,))
            return cursor.rowcount > 0