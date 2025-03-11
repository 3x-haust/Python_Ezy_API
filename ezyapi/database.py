from abc import ABC, abstractmethod
from typing import Type, List, Optional, Generic, TypeVar, Dict, Any
import sqlite3
import inflect
import psycopg2
import psycopg2.extras
import sys
from motor.motor_asyncio import AsyncIOMotorClient
import pymysql
from urllib.parse import urlparse

T = TypeVar('T')

class Not:
    def __init__(self, value: Any):
        self.value = value

class LessThan:
    def __init__(self, value: Any):
        self.value = value

class LessThanOrEqual:
    def __init__(self, value: Any):
        self.value = value

class MoreThan:
    def __init__(self, value: Any):
        self.value = value

class MoreThanOrEqual:
    def __init__(self, value: Any):
        self.value = value

class Equal:
    def __init__(self, value: Any):
        self.value = value

class Like:
    def __init__(self, value: str):
        self.value = value

class ILike:
    def __init__(self, value: str):
        self.value = value

class Between:
    def __init__(self, min: Any, max: Any):
        self.min = min
        self.max = max

class In:
    def __init__(self, values: List[Any]):
        self.values = values

class IsNull:
    def __init__(self):
        pass

class EzyRepository(Generic[T], ABC):
    async def find(self, where: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None, select: Optional[List[str]] = None, relations: Optional[Dict[str, Any]] = None, order: Optional[Dict[str, str]] = None, skip: Optional[int] = None, take: Optional[int] = None) -> List[T]:
        pass
    async def find_one(self, where: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None, select: Optional[List[str]] = None, relations: Optional[Dict[str, Any]] = None) -> Optional[T]:
        pass
    async def save(self, entity: T) -> T:
        pass
    async def delete(self, id: int) -> bool:
        pass

class SQLiteRepository(EzyRepository[T]):
    def __init__(self, db_path: str, entity_class: Type[T]):
        self.db_path = db_path
        self.entity_class = entity_class
        self.table_name = self._get_table_name(entity_class)
        self._ensure_table_exists()
    def _get_table_name(self, entity_class: Type[T]) -> str:
        p = inflect.engine()
        name = entity_class.__name__
        if name.endswith("Entity"):
            name = name[:-6]
        return p.plural(name.lower())
    def _get_conn(self):
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
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {self.table_name} ({', '.join(columns)});"
        with self._get_conn() as conn:
            conn.execute(create_table_sql)
    async def find(self, where: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None, select: Optional[List[str]] = None, relations: Optional[Dict[str, Any]] = None, order: Optional[Dict[str, str]] = None, skip: Optional[int] = None, take: Optional[int] = None) -> List[T]:
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
            return [self._row_to_entity(row) for row in rows]
    async def find_one(self, where: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None, select: Optional[List[str]] = None, relations: Optional[Dict[str, Any]] = None) -> Optional[T]:
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
            return self._row_to_entity(row) if row else None
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
        entity = self.entity_class()
        for key in row.keys():
            setattr(entity, key, row[key])
        return entity
    def _build_where_clause(self, conditions: Dict[str, Any]) -> tuple[List[str], List[Any]]:
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

class PostgreSQLRepository(EzyRepository[T]):
    def __init__(self, connection_string: str, entity_class: Type[T]):
        self.connection_string = connection_string
        self.entity_class = entity_class
        self.table_name = self._get_table_name(entity_class)
        self._ensure_table_exists()
    def _get_table_name(self, entity_class: Type[T]) -> str:
        p = inflect.engine()
        name = entity_class.__name__
        if name.endswith("Entity"):
            name = name[:-6]
        return p.plural(name.lower())
    def _get_conn(self):
        conn = psycopg2.connect(self.connection_string)
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
    async def find(self, where: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None, select: Optional[List[str]] = None, relations: Optional[Dict[str, Any]] = None, order: Optional[Dict[str, str]] = None, skip: Optional[int] = None, take: Optional[int] = None) -> List[T]:
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
    async def find_one(self, where: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None, select: Optional[List[str]] = None, relations: Optional[Dict[str, Any]] = None) -> Optional[T]:
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
        conn = self._get_conn()
        cursor = conn.cursor()
        query = f"DELETE FROM {self.table_name} WHERE id = %s;"
        cursor.execute(query, (id,))
        conn.commit()
        rowcount = cursor.rowcount
        cursor.close()
        conn.close()
        return rowcount > 0
    def _row_to_entity(self, row) -> T:
        entity = self.entity_class()
        for key in row.keys():
            setattr(entity, key, row[key])
        return entity

class MongoDBRepository(EzyRepository[T]):
    def __init__(self, connection_string: str, entity_class: Type[T]):
        self.client = AsyncIOMotorClient(connection_string)
        self.db = self.client.get_default_database()
        self.entity_class = entity_class
        self.collection_name = self._get_collection_name(entity_class)
    def _get_collection_name(self, entity_class: Type[T]) -> str:
        p = inflect.engine()
        name = entity_class.__name__
        if name.endswith("Entity"):
            name = name[:-6]
        return p.plural(name.lower())
    def _build_filter(self, conditions: Dict[str, Any]) -> dict:
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
        entity = self.entity_class()
        for key, value in doc.items():
            if key == "_id":
                setattr(entity, "id", value)
            else:
                setattr(entity, key, value)
        return entity
    async def find(self, where: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None, select: Optional[List[str]] = None, relations: Optional[Dict[str, Any]] = None, order: Optional[Dict[str, str]] = None, skip: Optional[int] = None, take: Optional[int] = None) -> List[T]:
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
    async def find_one(self, where: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None, select: Optional[List[str]] = None, relations: Optional[Dict[str, Any]] = None) -> Optional[T]:
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
        collection = self.db[self.collection_name]
        result = await collection.delete_one({"_id": id})
        return result.deleted_count > 0

class MySQLRepository(EzyRepository[T]):
    def __init__(self, connection_string: str, entity_class: Type[T]):
        self.connection_string = connection_string
        self.entity_class = entity_class
        self.table_name = self._get_table_name(entity_class)
        self._ensure_table_exists()
    def _get_table_name(self, entity_class: Type[T]) -> str:
        p = inflect.engine()
        name = entity_class.__name__
        if name.endswith("Entity"):
            name = name[:-6]
        return p.plural(name.lower())
    def _get_conn(self):
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
    async def find(self, where: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None, select: Optional[List[str]] = None, relations: Optional[Dict[str, Any]] = None, order: Optional[Dict[str, str]] = None, skip: Optional[int] = None, take: Optional[int] = None) -> List[T]:
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
        return [self._row_to_entity(row) for row in rows]
    async def find_one(self, where: Optional[Dict[str, Any] | List[Dict[str, Any]]] = None, select: Optional[List[str]] = None, relations: Optional[Dict[str, Any]] = None) -> Optional[T]:
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
        return self._row_to_entity(row) if row else None
    async def save(self, entity: T) -> T:
        conn = self._get_conn()
        cursor = conn.cursor()
        attrs = {k: v for k, v in entity.__dict__.items() if not k.startswith('_')}
        if getattr(entity, 'id', None) is None:
            columns = ', '.join(k for k in attrs.keys() if k != 'id')
            placeholders = ', '.join('%s' for _ in range(len(attrs) - (1 if 'id' in attrs else 0)))
            values = [v for k, v in attrs.items() if k != 'id']
            query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders});"
            cursor.execute(query, values)
            entity.id = cursor.lastrowid
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
        conn = self._get_conn()
        cursor = conn.cursor()
        query = f"DELETE FROM {self.table_name} WHERE id = %s;"
        cursor.execute(query, (id,))
        conn.commit()
        rowcount = cursor.rowcount
        cursor.close()
        conn.close()
        return rowcount > 0
    def _row_to_entity(self, row) -> T:
        entity = self.entity_class()
        for key, value in row.items():
            setattr(entity, key, value)
        return entity

class EzyEntityBase:
    id: int = None

class EzyService:
    def __init__(self, repository: Optional[EzyRepository] = None):
        self.repository = repository

class DatabaseConfig:
    def __init__(self, db_type: str = "sqlite", connection_string: str = None, connection_params: dict = None):
        self.db_type = db_type
        self.connection_string = connection_string
        self.connection_params = connection_params or {}
        
        if not connection_string and not connection_params:
            if db_type == "sqlite":
                self.connection_string = ":memory:"
            else:
                raise ValueError(f"Either connection_string or connection_params must be provided for {db_type}")
        
        self._session_factory = None
    
    def get_connection_string(self):
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
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def get_repository(self, entity_class: Type[T]) -> EzyRepository[T]:
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
            raise ValueError(f"Unsupported database type: {self.db_type}")

def auto_inject_repository(service_class: Type[EzyService], db_config: DatabaseConfig):
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