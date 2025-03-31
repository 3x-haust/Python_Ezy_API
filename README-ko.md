이 README는 한국어 버전입니다.  
[Click here for the English version.](./README.md)

![Contributors](https://img.shields.io/github/contributors/3x-haust/Python_Ezy_API?style=flat)
![Forks](https://img.shields.io/github/forks/3x-haust/Python_Ezy_API?style=social?style=flat)
[![Stars](https://img.shields.io/github/stars/3x-haust/Python_Ezy_API?style=flat&logo=GitHub&color=yellow)](https://github.com/3x-haust/Python_Ezy_API/stargazers)
![License](https://img.shields.io/github/license/3x-haust/Python_Ezy_API?style=flat)
[![PyPI](https://img.shields.io/pypi/v/ezyapi?logo=PyPI?style=flat)](https://pypi.org/project/ezyapi/)

</br>

# 목차
- [목차](#목차)
- [기여 방법](#기여-방법)
  - [브랜치 생성하기](#브랜치-생성하기)
    - [브랜치 네이밍 규칙](#브랜치-네이밍-규칙)
  - [작업하고 커밋하기](#작업하고-커밋하기)
    - [커밋 메시지 컨벤션](#커밋-메시지-컨벤션)
    - [커밋 예시](#커밋-예시)
  - [원격 저장소로 푸시](#원격-저장소로-푸시)
  - [Pull Request(PR) 올리기](#pull-requestpr-올리기)
  - [머지하기](#머지하기)
- [첫 번째 단계](#첫-번째-단계)
    - [배경](#배경)
    - [시작하기](#시작하기)
      - [언어](#언어)
      - [전제조건](#전제조건)
      - [설정하기](#설정하기)
    - [어플리케이션 실행하기](#어플리케이션-실행하기)
- [서비스](#서비스)
    - [서비스란?](#서비스란)
    - [서비스 구조](#서비스-구조)
    - [URL 매핑 규칙](#url-매핑-규칙)
    - [서비스 등록](#서비스-등록)
    - [경로 파라미터 예시](#경로-파라미터-예시)
    - [쿼리 파라미터 예시](#쿼리-파라미터-예시)
    - [데코레이터 예시 (@route)](#데코레이터-예시-route)
- [CLI 개요](#cli-개요)

</br>
</br>
</br>

# 기여 방법

Ezy API는 누구나 자유롭게 기여할 수 있습니다!  
아래 절차를 따라 편하게 참여해 주세요.

## 브랜치 생성하기

새로운 작업을 시작할 때는 **브랜치**를 만들어 주세요. 브랜치는 보통 `feature/{기능명}` 형태로 작성합니다.

```bash
# 메인(main) 브랜치로 이동 후 최신 상태로 맞추기
$ git checkout main
$ git pull origin main

# 새 브랜치 생성 및 이동
$ git checkout -b feature/기능명
```

### 브랜치 네이밍 규칙

작업 성격에 맞게 브랜치명을 작성해 주세요.

| 타입 | 설명 | 예시 |
|:---:|:---|:---|
| `feature/` | 새로운 기능 개발 | `feature/login-api`, `feature/add-user-api` |
| `fix/` | 버그 수정 | `fix/login-bug`, `fix/routing-error` |
| `docs/` | 문서 작업 (README, 주석 등) | `docs/update-readme`, `docs/api-docs` |
| `refactor/` | 코드 리팩토링 | `refactor/login-service`, `refactor/db-helper` |
| `test/` | 테스트 코드 추가 및 수정 | `test/user-service-test` |
| `chore/` | 빌드 설정, 패키지 관리, 기타 잡무 | `chore/update-deps`, `chore/ci-config` |

> **팁**
> 
> 브랜치명은 작업 내용을 명확하게 드러내는 것이 좋습니다.


## 작업하고 커밋하기

작업을 마친 뒤, 커밋 메시지는 아래 **커밋 컨벤션**을 참고하여 작성해 주세요.

### 커밋 메시지 컨벤션

| 태그 | 설명 |
|:---:|:---|
| `feat` | 새로운 기능 추가 |
| `fix` | 버그 수정 |
| `docs` | 문서 수정 (README, 주석 등) |
| `style` | 코드 포맷팅, 스펠링 수정 등 코드에 영향을 주지 않는 변경 |
| `refactor` | 코드 리팩토링 (동작 변화 없이 내부 로직 개선) |
| `test` | 테스트 코드 추가 및 수정 |
| `chore` | 빌드 업무, 패키지 매니저 설정, 유지보수 작업 등 |

### 커밋 예시
```bash
$ git commit -m "feat: 사용자 API 추가"
$ git commit -m "fix: 잘못된 라우터 경로 수정"
$ git commit -m "docs: README에 설치 방법 추가"
```

## 원격 저장소로 푸시

작성한 브랜치를 원격 저장소에 푸시합니다.

```bash
$ git push origin feature/기능명
```

## Pull Request(PR) 올리기

- GitHub에서 **Pull Request**를 생성합니다.
- 어떤 작업을 했는지 PR 설명란에 간단하게 적어주세요.
- 이후 팀원들과 코드 리뷰를 진행합니다.

## 머지하기

- 리뷰가 끝나고 승인을 받으면 **main 브랜치로 머지**합니다.
- 머지 후에는 다른 작업 전에 항상 `main` 브랜치를 최신으로 맞춰주세요.

```bash
$ git checkout main
$ git pull origin main
```

</br>
</br>
</br>

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

</br>
</br>
</br>

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

> **팁**  
> 
> `@route()` 데코레이터를 사용하면 자동 매핑을 오버라이드하여 원하는 URL, HTTP 메서드를 자유롭게 설정할 수 있습니다.

</br>
</br>
</br>

# CLI 개요
