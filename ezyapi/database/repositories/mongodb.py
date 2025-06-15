"""
MongoDB 저장소 모듈

이 모듈은 MongoDB 데이터베이스에 대한 저장소 구현을 제공합니다.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, List, Optional, Any, Type, TypeVar, get_type_hints

from ezyapi.database.repositories.base import EzyRepository
from ezyapi.database.filters import (
    Not, LessThan, LessThanOrEqual, MoreThan, MoreThanOrEqual,
    Equal, Like, ILike, Between, In, IsNull
)
from ezyapi.utils.inflection import get_table_name_from_entity

T = TypeVar('T')

class MongoDBRepository(EzyRepository[T]):
    """
    MongoDB 데이터베이스를 위한 저장소 구현
    
    이 클래스는 EzyRepository 인터페이스를 구현하여 MongoDB 데이터베이스에 
    데이터를 저장하고 접근하는 기능을 제공합니다.
    """
    
    def __init__(self, connection_string: str, entity_class: Type[T]):
        """
        MongoDB 저장소 초기화
        
        Args:
            connection_string (str): MongoDB 데이터베이스 연결 문자열
            entity_class (Type[T]): 이 저장소가 관리할 엔티티 클래스
        """
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client.get_default_database()
        self.entity_class = entity_class
        self.collection_name = get_table_name_from_entity(entity_class)
    
    def _build_filter(self, conditions: Dict[str, Any]) -> dict:
        """
        조건 딕셔너리에서 MongoDB 필터를 구성합니다.
        
        Args:
            conditions (Dict[str, Any]): 검색 조건
            
        Returns:
            dict: MongoDB 쿼리 필터
        """
        f = {}
        
        for key, value in conditions.items():
            if isinstance(value, Not):
                f[key] = {"$ne": value.value}
            elif isinstance(value, LessThan):
                f[key] = {"$lt": value.value}
            elif isinstance(value, LessThanOrEqual):
                f[key] = {"$lte": value.value}
            elif isinstance(value, MoreThan):
                f[key] = {"$gt": value.value}
            elif isinstance(value, MoreThanOrEqual):
                f[key] = {"$gte": value.value}
            elif isinstance(value, Equal):
                f[key] = value.value
            elif isinstance(value, Like):
                f[key] = {"$regex": value.value}
            elif isinstance(value, ILike):
                f[key] = {"$regex": value.value, "$options": "i"}
            elif isinstance(value, Between):
                f[key] = {"$gte": value.min, "$lte": value.max}
            elif isinstance(value, In):
                f[key] = {"$in": value.values}
            elif isinstance(value, IsNull):
                f[key] = None
            else:
                f[key] = value
                
        return f
    
    def _doc_to_entity(self, doc: dict) -> T:
        """
        MongoDB 문서를 엔티티 객체로 변환합니다.
        
        Args:
            doc (dict): MongoDB 문서
            
        Returns:
            T: 변환된 엔티티 객체
        """
        entity = self.entity_class()
        
        for key, value in doc.items():
            if key == "_id":
                setattr(entity, "id", value)
            else:
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
                                '_mapped_by': f"{self.collection_name}_id"
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
            
            target_collection = get_table_name_from_entity(target_entity)
            
            if relation_type == 'many_to_one':
                foreign_key = relation_info.get('_foreign_key', f"{relation_name}_id")
                await self._load_many_to_one_relation(entities, relation_name, target_entity, target_collection, foreign_key)
                
            elif relation_type == 'one_to_many':
                mapped_by = relation_info.get('_mapped_by', f"{self.collection_name}_id")
                await self._load_one_to_many_relation(entities, relation_name, target_entity, target_collection, mapped_by)
        
        return entities
    
    async def _load_many_to_one_relation(self, entities: List[T], relation_name: str, 
                                       target_entity: Type, target_collection: str, foreign_key: str):
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
        
        collection = self.db[target_collection]
        related_docs = await collection.find({"_id": {"$in": unique_fk_values}}).to_list(length=None)
        
        related_entities = {}
        for doc in related_docs:
            related_entity = target_entity()
            for key, value in doc.items():
                if key == "_id":
                    setattr(related_entity, "id", value)
                else:
                    setattr(related_entity, key, value)
            related_entities[doc['_id']] = related_entity
        
        for entity in entities:
            fk_value = getattr(entity, foreign_key, None)
            if fk_value in related_entities:
                setattr(entity, relation_name, related_entities[fk_value])
    
    async def _load_one_to_many_relation(self, entities: List[T], relation_name: str,
                                       target_entity: Type, target_collection: str, mapped_by: str):
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
        
        collection = self.db[target_collection]
        related_docs = await collection.find({mapped_by: {"$in": unique_parent_ids}}).to_list(length=None)
        
        children_by_parent = {}
        for doc in related_docs:
            related_entity = target_entity()
            for key, value in doc.items():
                if key == "_id":
                    setattr(related_entity, "id", value)
                else:
                    setattr(related_entity, key, value)
            
            parent_id = doc[mapped_by]
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
        collection = self.db[self.collection_name]
        f = {}
        
        if where:
            if isinstance(where, list):
                f = {"$or": [self._build_filter(cond) for cond in where]}
            else:
                f = self._build_filter(where)
                
        projection = None
        if select:
            projection = {field: 1 for field in select}
            
        cursor = collection.find(f, projection)
        
        if order:
            sort_list = [(k, 1 if v.lower() == "asc" else -1) for k, v in order.items()]
            cursor = cursor.sort(sort_list)
            
        if skip:
            cursor = cursor.skip(skip)
            
        if take:
            cursor = cursor.limit(take)
            
        docs = await cursor.to_list(length=take or 100)
        entities = [self._doc_to_entity(doc) for doc in docs]
        
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
            relations: 함께 로드할 관계 데이터. 예: ["user", "posts"]
            
        Returns:
            Optional[T]: 검색된 엔티티 또는 None
        """
        collection = self.db[self.collection_name]
        f = {}
        
        if where:
            if isinstance(where, list):
                f = {"$or": [self._build_filter(cond) for cond in where]}
            else:
                f = self._build_filter(where)
                
        projection = None
        if select:
            projection = {field: 1 for field in select}
            
        doc = await collection.find_one(f, projection)
        entity = self._doc_to_entity(doc) if doc else None
        
        if entity and relations:
            entity = await self._load_relations([entity], relations)
            entity = entity[0] if entity else None
            
        return entity
    
    async def save(self, entity: T) -> T:
        """
        엔티티를 저장합니다. primary key가 없으면 생성하고, 있으면 업데이트합니다.
        
        Args:
            entity: 저장할 엔티티 인스턴스
            
        Returns:
            T: 저장된 엔티티
        """
        collection = self.db[self.collection_name]
        data = entity.__dict__.copy()
        
        pk_info = entity.get_primary_key_info()
        pk_field = pk_info['field_name']
        pk_auto_increment = pk_info['auto_increment']
        
        pk_value = getattr(entity, pk_field, None)
        
        if pk_field == 'id':
            mongo_pk_field = '_id'
        else:
            mongo_pk_field = pk_field
        
        if pk_auto_increment and pk_value is None:
            data.pop(pk_field, None)
            result = await collection.insert_one(data)
            setattr(entity, pk_field, result.inserted_id)
        elif not pk_auto_increment and pk_value is None:
            raise ValueError(f"Primary key '{pk_field}' 값이 필요합니다.")
        elif pk_value is not None:
            filter_dict = {mongo_pk_field: pk_value}
            data_to_save = {k: v for k, v in data.items() if k != pk_field}
            
            await collection.update_one(
                filter_dict, 
                {"$set": data_to_save},
                upsert=True
            )
            
        return entity
    
    async def delete(self, pk_value: Any) -> bool:
        """
        지정된 primary key 값의 엔티티를 삭제합니다.
        
        Args:
            pk_value: 삭제할 엔티티의 primary key 값
            
        Returns:
            bool: 삭제 성공 여부
        """
        collection = self.db[self.collection_name]
        
        entity_instance = self.entity_class()
        pk_info = entity_instance.get_primary_key_info()
        pk_field = pk_info['field_name']
        
        if pk_field == 'id':
            mongo_pk_field = '_id'
        else:
            mongo_pk_field = pk_field
        
        result = await collection.delete_one({mongo_pk_field: pk_value})
        return result.deleted_count > 0