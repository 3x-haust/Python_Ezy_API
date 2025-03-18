이 README는 한국어 버전입니다.  
[Click here for the English version.](./README.md)

# 첫 번째 단계

### 배경

저희는 [Nest.js](https://nestjs.com/)를 좋아하지만, [Nest.js](https://nestjs.com/)의 Controller, Module 등이 간단한 작업에는 불필요하다고 생각했습니다.

### 시작하기

이 문서에서는 Ezy API의 **핵심 원리** 에 대해 알아봅니다. Ezy API 애플리케이션의 필수 구성 요소를 숙지하려면,
기초적인 수준에서 많은 분야를 다루며 기본적인 CRUD 애플리케이션을 구축해 봐야 합니다.

#### 언어

Ezy API는 [Python](https://www.python.org/)언어를 사용합니다.

추후에는 [TypeScript](https://www.typescriptlang.org/), [Java](https://java.com/) 등과 같은 언어에서 사용할 수 있도록 지원할 예정입니다.

#### 전제조건

운영 체제에 [Python](https://www.python.org/)(>= 3.6)가 설치되어 있는지 확인하세요.

#### 설정하기

[Ezy API CLI](#cli-개요) 로 새 프로젝트를 설정하는 것은 매우 간단합니다. [pip](https://pypi.org/project/pip/)이 설치되어 있다면, OS 터미널에서 다음 명령을 사용해 새 Ezy API 프로젝트를 생성할 수 있습니다.


```bash
$ pip install ezyapi
$ ezy new project-name
```

`project-name` 디렉토리가 생성되고, main.py 와 cli 설정 파일들이 생성됩니다.

프로젝트의 기본적인 구조는 아래와 같습니다.
```
app_service.py
ezy.json
main.py
```
> **팁**
> 
> 위의 파일은 [이곳에서](https://github.com/3x-haust/Python_Ezy_API/tree/main/example) 확인할 수 있습니다.

<br></br>

위 핵심 파일들을 간단하게 설명하면 아래와 같습니다.

|파일명|설명|
|:---:|:---|
|`app_service.py`|기본적인 서비스 파일|
|`ezy.json`|cli 명령어 설정 파일|
|`main.py`|시작 파일(entry file). 핵심 함수인 `EzyAPI`를 사용하여 Ezy API 어플리케이션 인스턴스를 만듭니다.|

> 위에서 서술한 서비스 등은 지금은 이해 못하셔도 괜찮습니다. 이후에 나올 챕터들에서 자세한 설명이 나옵니다!

<br><br/>

간단하게 main.py 파일부터 만들어 보겠습니다. 해당 파일에는 어플리케이션을 시작해주는 main 모듈이 있습니다.

```python
# main.py
from ezyapi import EzyAPI
from ezyapi.database import DatabaseConfig
from user.user_service import UserService
from app_service import AppService

if __name__ == "__main__":
    app = EzyAPI()
    app.run(port=8000)
```

### 어플리케이션 실행하기

OS 터미널에서 다음 명령을 어플리케이션을 실행할 수 있습니다
```bash
$ ezy run start
```

# 서비스

### 서비스란?

Ezy API에서 **서비스(Service)** 는 요청을 처리하고 비즈니스 로직을 수행하는 핵심 구성 요소입니다.  
[Nest.js](https://nestjs.com)의 Controller나 Service와 비슷한 역할을 하지만, Ezy API는 더 간결하고 직관적인 방식으로 서비스만으로도 충분히 API를 구성할 수 있도록 설계되었습니다.

### 서비스 구조

서비스는 `EzyService` 클래스를 상속받아 생성됩니다.  
아래는 기본적인 서비스의 예시입니다.
> **팁**
>
> 서비스는 ```$ ezy g res user``` 사용해 생성 할 수 있습니다

```python
# app_service.py
from ezyapi import EzyService

class AppService(EzyService):
    async def get_app(self) -> str:
        return "Hello, World!"
```

- `EzyService`를 상속하면, 서비스 내에서 비동기 함수로 API 엔드포인트를 정의할 수 있습니다.
- 함수명은 곧 API의 엔드포인트 URL이 됩니다.
  - 예를 들어 `get_user`이라는 함수는 `/user/` 경로에 `GET`메소드로 자동 매핑됩니다.
    - 단 예외적으로 서비스 명이 `app`인 경우에는 루트 경로로 매핑 됩니다.
- 함수는 `async`로 정의하여 비동기 처리가 가능합니다.

### URL 매핑 규칙

서비스의 함수 이름이 URL 엔드포인트로 자동으로 매핑됩니다.

| 함수명 | HTTP 메서드 | URL |
|:---:|:---:|:---|
|`get_user`|GET|`/user/`|
|`list_users`|GET|`/user/`|
|`create_user`|POST|`/user/`|
|`update_user`|PUT|`/user/`|
|`delete_user`|DELETE|`/user/`|
|`edit_user`|PATCH|`/user/`|

> **팁**
> 
> `get`, `update`, `delete`, `edit` 메소드들은 `by_id` 등을 이용하여 `경로 파라미터를 이용할 수 있습니다` 
> 예: `get_user_by_id` ➡️ `GET /user/{id}`

### 서비스 등록

서비스는 `main.py`에서 EzyAPI 인스턴스에 등록할 수 있습니다.

```python
# main.py
from ezyapi import EzyAPI
from ezyapi.database import DatabaseConfig
from app_service import AppService

if __name__ == "__main__":
    app.add_service(AppService)
    app.run(port=8000)
```
---

### 경로 파라미터 예시

Ezy API는 함수명에 `by_id`, `by_name` 등을 붙이면 URL 경로에 파라미터를 자동으로 매핑합니다.

```python
# user_service.py
from ezyapi import EzyService

class UserService(EzyService):
    async def get_user_by_id(self, id: int) -> dict:
        return {"id": id, "name": "John Doe"}
```

- `get_user_by_id` ➡️ `GET /user/{id}` 경로로 자동 매핑됩니다.
- `id`는 URL 경로에서 `path parameter`로 사용됩니다.

**요청 예시**
```http
GET /user/10
```

**응답 예시**
```json
{
  "id": 10,
  "name": "John Doe"
}
```

### 쿼리 파라미터 예시

쿼리 파라미터는 함수 인자에서 `Optional`과 기본값을 정의하면, 쿼리 스트링으로 받을 수 있습니다.

```python
# user_service.py
from ezyapi import EzyService
from typing import Optional, List

class UserService(EzyService):
    async def list_users(self, name: Optional[str] = None, age: Optional[int] = None) -> List[dict]:
        filters = {}
        if name:
            filters["name"] = name
        if age:
            filters["age"] = age

        return [{"id": 1, "name": name or "John", "age": age or 25}]
```

- `list_users` ➡️ `GET /user/`
- 쿼리스트링으로 `name`, `age`를 전달할 수 있습니다.

**요청 예시**
```http
GET /user/?name=Alice&age=30
```

**응답 예시**
```json
[
  {
    "id": 1,
    "name": "Alice",
    "age": 30
  }
]
```

---

### 데코레이터 예시 (@route)

서비스 함수에 직접 `@route()` 데코레이터를 사용하면 URL과 메서드를 수동으로 지정할 수 있습니다.

```python
# user_service.py
from ezyapi import EzyService
from ezyapi.core import route

class UserService(EzyService):
    @route('get', '/name/{name}', description="Get user by name")
    async def get_user_by_name(self, name: str) -> dict:
        return {"name": name, "email": "example@example.com"}
```

- `@route('get', '/name/{name}')` ➡️ `GET /name/{name}` 경로로 설정됩니다.
- `description`은 API 문서화에 사용됩니다.

**요청 예시**
```http
GET /name/Alice
```

**응답 예시**
```json
{
  "name": "Alice",
  "email": "example@example.com"
}
```

> **참고**  
> `@route()` 데코레이터를 사용하면 자동 매핑을 오버라이드하여 원하는 URL, HTTP 메서드를 자유롭게 설정할 수 있습니다.


# CLI 개요


