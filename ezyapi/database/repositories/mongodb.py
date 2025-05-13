"""
MongoDB 저장소 모듈

이 모듈은 MongoDB 데이터베이스에 대한 저장소 구현을 제공합니다.
"""

from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, List, Optional, Any, Type, TypeVar

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
            relations: 함께 로드할 관계 데이터 (MongoDB에서는 구현되지 않음)
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
        return [self._doc_to_entity(doc) for doc in docs]
    
    async def find_one(self, 
                      where: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None, 
                      select: Optional[List[str]] = None, 
                      relations: Optional[Dict[str, Any]] = None) -> Optional[T]:
        """
        조건에 맞는 단일 엔티티를 검색합니다.
        
        Args:
            where: 검색 조건
            select: 선택할 필드 목록
            relations: 함께 로드할 관계 데이터 (MongoDB에서는 구현되지 않음)
            
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
        return self._doc_to_entity(doc) if doc else None
    
    async def save(self, entity: T) -> T:
        """
        엔티티를 저장합니다. id가 없으면 생성하고, 있으면 업데이트합니다.
        
        Args:
            entity: 저장할 엔티티 인스턴스
            
        Returns:
            T: 저장된 엔티티
        """
        collection = self.db[self.collection_name]
        data = entity.__dict__.copy()
        
        if data.get("id") is None:
            data.pop("id", None)
            result = await collection.insert_one(data)
            entity.id = result.inserted_id
        else:
            id_val = entity.id
            data.pop("id", None)
            await collection.update_one({"_id": id_val}, {"$set": data})
            
        return entity
    
    async def delete(self, id: int) -> bool:
        """
        지정된 ID의 엔티티를 삭제합니다.
        
        Args:
            id: 삭제할 엔티티의 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        collection = self.db[self.collection_name]
        result = await collection.delete_one({"_id": id})
        return result.deleted_count > 0