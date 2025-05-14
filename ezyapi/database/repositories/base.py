"""
저장소 기본 클래스 모듈

이 모듈은 데이터 접근을 위한 저장소 인터페이스를 정의합니다.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Generic, TypeVar, Type

T = TypeVar('T')

class EzyRepository(Generic[T], ABC):
    """
    데이터베이스 저장소의 기본 추상 클래스
    
    이 클래스는 모든 저장소 구현체가 따라야 하는 기본 인터페이스를 정의합니다.
    제네릭 타입 T는 저장소가 관리하는 엔티티의 타입입니다.
    
    """
    
    @abstractmethod
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
            relations: 함께 로드할 관계 데이터
            order: 정렬 조건
            skip: 건너뛸 결과 수
            take: 가져올 결과 수
            
        Returns:
            List[T]: 검색된 엔티티 목록
        """
        pass
    
    @abstractmethod
    async def find_one(self, 
                      where: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None, 
                      select: Optional[List[str]] = None, 
                      relations: Optional[Dict[str, Any]] = None) -> Optional[T]:
        """
        조건에 맞는 단일 엔티티를 검색합니다.
        
        Args:
            where: 검색 조건
            select: 선택할 필드 목록
            relations: 함께 로드할 관계 데이터
            
        Returns:
            Optional[T]: 검색된 엔티티 또는 None
        """
        pass
    
    @abstractmethod
    async def save(self, entity: T) -> T:
        """
        엔티티를 저장합니다. id가 없으면 생성하고, 있으면 업데이트합니다.
        
        Args:
            entity: 저장할 엔티티 인스턴스
            
        Returns:
            T: 저장된 엔티티
        """
        pass
    
    @abstractmethod
    async def delete(self, id: int) -> bool:
        """
        지정된 ID의 엔티티를 삭제합니다.
        
        Args:
            id: 삭제할 엔티티의 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        pass