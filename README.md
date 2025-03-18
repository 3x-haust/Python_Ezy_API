물론이죠! 아래는 요청하신 README의 영어 버전입니다:

---

This is the Korean version of the README.  
[여기를 클릭하여 한국어 버전을 확인하세요.](./README_ko.md)

# First Steps

### Background

We love [Nest.js](https://nestjs.com/), but we felt that Controllers and Modules in [Nest.js](https://nestjs.com/) can be excessive for simple tasks.

### Getting Started

In this document, you will learn about the **core principles** of Ezy API. To fully understand the essential components of an Ezy API application, we will cover a broad range of basic topics and build a simple CRUD application.

#### Language

Ezy API is built using the [Python](https://www.python.org/) programming language.

We plan to support other languages such as [TypeScript](https://www.typescriptlang.org/) and [Java](https://java.com/) in the future.

#### Prerequisites

Ensure that you have [Python](https://www.python.org/) (>= 3.6) installed on your operating system.

#### Setup

Setting up a new project with the [Ezy API CLI](#cli-overview) is very simple. If you have [pip](https://pypi.org/project/pip/) installed, you can create a new Ezy API project from your terminal using the following commands:

```bash
$ pip install ezyapi
$ ezy new project-name
```

This will create a `project-name` directory containing `main.py` and CLI configuration files.

The basic structure of the project will look like this:
```
app_service.py
ezy.json
main.py
```

> **Tip**
> 
> You can check out the above files [here](https://github.com/3x-haust/Python_Ezy_API/tree/main/example).

<br></br>

Here’s a brief explanation of these core files:

|Filename|Description|
|:---:|:---|
|`app_service.py`|Basic service file|
|`ezy.json`|CLI command configuration file|
|`main.py`|Entry file. Creates an Ezy API application instance using the `EzyAPI` core function.|

> Don’t worry if you don’t fully understand services yet! Detailed explanations will follow in the next chapters.

<br><br/>

Let’s start by creating a simple `main.py` file, which contains the main module to launch the application.

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

### Running the Application

You can run the application from your terminal with the following command:
```bash
$ ezy run start
```

# Service

### What is a Service?

In Ezy API, a **Service** is a core component that handles requests and executes business logic.  
It plays a similar role to Controllers or Services in [Nest.js](https://nestjs.com/), but Ezy API is designed to be more concise and intuitive, allowing you to build APIs using services alone.

### Service Structure

A service is created by extending the `EzyService` class.  
Here’s an example of a basic service:

```python
# app_service.py
from ezyapi import EzyService

class AppService(EzyService):
    async def get_app(self) -> str:
        return "Hello, World!"
```

- By extending `EzyService`, you can define API endpoints directly as asynchronous functions inside the service.
- The function name automatically becomes the API endpoint URL.
  - For example, a function named `get_user` will automatically map to the `GET` method at `/user/`.
  - If the service name is `app`, it will map to the root (`/`) path.
- Functions should be defined as `async` for asynchronous processing.

### URL Mapping Rules

Function names are automatically mapped to URL endpoints as follows:

| Function | HTTP Method | URL |
|:---:|:---:|:---|
|`get_user`|GET|`/user/`|
|`list_users`|GET|`/user/`|
|`create_user`|POST|`/user/`|
|`update_user`|PUT|`/user/`|
|`delete_user`|DELETE|`/user/`|
|`edit_user`|PATCH|`/user/`|

> **Tip**
> 
> Methods like `get`, `update`, `delete`, and `edit` can use route parameters such as `by_id`.
> Example: `get_user_by_id` ➡️ `GET /user/{id}`

### Registering a Service

You can register your service in `main.py` by adding it to the EzyAPI instance.

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

### Example: Path Parameters

In Ezy API, adding `by_id`, `by_name`, etc., to a function name will automatically map it to a URL path parameter.

```python
# user_service.py
from ezyapi import EzyService

class UserService(EzyService):
    async def get_user_by_id(self, id: int) -> dict:
        return {"id": id, "name": "John Doe"}
```

- `get_user_by_id` ➡️ automatically maps to `GET /user/{id}`.
- The `id` parameter is extracted from the URL path.

**Request Example**
```http
GET /user/10
```

**Response Example**
```json
{
  "id": 10,
  "name": "John Doe"
}
```

### Example: Query Parameters

You can define optional parameters to accept query strings.

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

- `list_users` ➡️ maps to `GET /user/`.
- `name` and `age` can be passed via query strings.

**Request Example**
```http
GET /user/?name=Alice&age=30
```

**Response Example**
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

### Example: @route Decorator

You can use the `@route()` decorator to manually define URLs and HTTP methods.

```python
# user_service.py
from ezyapi import EzyService
from ezyapi.core import route

class UserService(EzyService):
    @route('get', '/name/{name}', description="Get user by name")
    async def get_user_by_name(self, name: str) -> dict:
        return {"name": name, "email": "example@example.com"}
```

- `@route('get', '/name/{name}')` ➡️ sets the route to `GET /name/{name}`.
- `description` is used for API documentation.

**Request Example**
```http
GET /name/Alice
```

**Response Example**
```json
{
  "name": "Alice",
  "email": "example@example.com"
}
```

> **Note**  
> Using `@route()` overrides automatic mapping, allowing full control over URL and HTTP method.


# CLI Overview

---

필요하면 CLI 개요 부분도 영어로 이어서 번역해드릴까요?