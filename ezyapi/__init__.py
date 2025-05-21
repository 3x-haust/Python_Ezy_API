"""
Ezy API 패키지

Ezy API는 쉬운 API 생성 및 프로젝트 관리를 위한 프레임워크입니다.
"""

from ezyapi.api.core import EzyAPI
from ezyapi.service.base import EzyService
from ezyapi.database.entity import EzyEntityBase
from ezyapi.database.config import DatabaseConfig
from ezyapi.database.filters import (
    Not, LessThan, LessThanOrEqual, MoreThan, MoreThanOrEqual,
    Equal, Like, ILike, Between, In, IsNull
)
from ezyapi.decorators.route import route

__version__ = "1.3.0"
