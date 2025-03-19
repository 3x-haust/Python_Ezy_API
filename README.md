This is the Korean version of the README.  
[여기를 클릭하여 한국어 버전을 확인하세요.](./README-ko.md)

</br>
</br>
</br>

![Contributors](https://img.shields.io/github/contributors/3x-haust/Python_Ezy_API?style=flat)
![Forks](https://img.shields.io/github/forks/3x-haust/Python_Ezy_API?style=social?style=flat)
[![Stars](https://img.shields.io/github/stars/3x-haust/Python_Ezy_API?style=flat&logo=GitHub&color=yellow)](https://github.com/3x-haust/Python_Ezy_API/stargazers)
![License](https://img.shields.io/github/license/3x-haust/Python_Ezy_API?style=flat)
[![PyPI](https://img.shields.io/pypi/v/ezyapi?logo=PyPI?style=flat)](https://pypi.org/project/ezyapi/)

</br>
</br>
</br>

# Table of Contents

- [Table of Contents](#table-of-contents)
- [Contribution Guide](#contribution-guide)
  - [Create a Branch](#create-a-branch)
    - [Branch Naming Convention](#branch-naming-convention)
  - [Work and Commit](#work-and-commit)
    - [Commit Message Convention](#commit-message-convention)
    - [Commit Examples](#commit-examples)
  - [Push to Remote](#push-to-remote)
  - [Create a Pull Request (PR)](#create-a-pull-request-pr)
  - [Merge](#merge)
- [First Step](#first-step)
    - [Background](#background)
    - [Getting Started](#getting-started)
      - [Language](#language)
      - [Prerequisites](#prerequisites)
      - [Setup](#setup)
    - [Running the Application](#running-the-application)
- [Services](#services)
    - [What is a Service?](#what-is-a-service)
    - [Service Structure](#service-structure)
    - [URL Mapping Rules](#url-mapping-rules)
    - [Registering a Service](#registering-a-service)
    - [Path Parameter Example](#path-parameter-example)
    - [Query Parameter Example](#query-parameter-example)
    - [Decorator Example (@route)](#decorator-example-route)
- [CLI Overview](#cli-overview)

# Contribution Guide

Ezy API is open to contributions from everyone!  
Feel free to follow the steps below to participate.

## Create a Branch

When starting new work, please create a **branch**. Branches are usually named in the format `feature/{feature-name}`.

```bash
# Switch to the main branch and sync with the latest version
$ git checkout main
$ git pull origin main

# Create and switch to a new branch
$ git checkout -b feature/feature-name
```

### Branch Naming Convention

Name your branch according to the nature of your work.

| Type | Description | Example |
|:---:|:---|:---|
| `feature/` | New feature development | `feature/login-api`, `feature/add-user-api` |
| `fix/` | Bug fixes | `fix/login-bug`, `fix/routing-error` |
| `docs/` | Documentation (README, comments, etc.) | `docs/update-readme`, `docs/api-docs` |
| `refactor/` | Code refactoring | `refactor/login-service`, `refactor/db-helper` |
| `test/` | Adding or updating tests | `test/user-service-test` |
| `chore/` | Build settings, package management, miscellaneous tasks | `chore/update-deps`, `chore/ci-config` |

> **Tip**  
> Branch names should clearly indicate the purpose of the work.

## Work and Commit

After completing your work, write a commit message following the **commit convention** below.

### Commit Message Convention

| Tag | Description |
|:---:|:---|
| `feat` | Add a new feature |
| `fix` | Fix a bug |
| `docs` | Update documentation (README, comments, etc.) |
| `style` | Code formatting, typos, non-functional changes |
| `refactor` | Code refactoring (internal improvements without behavior change) |
| `test` | Add or update tests |
| `chore` | Build tasks, package manager configuration, maintenance work |

### Commit Examples
```bash
$ git commit -m "feat: add user API"
$ git commit -m "fix: fix incorrect router path"
$ git commit -m "docs: add installation guide to README"
```

## Push to Remote

Push your branch to the remote repository.

```bash
$ git push origin feature/feature-name
```

## Create a Pull Request (PR)

- Create a **Pull Request** on GitHub.
- Briefly describe what you worked on in the PR description.
- Then proceed with a code review with your team.

## Merge

- Once the review is complete and approved, **merge into the main branch**.
- After merging, always make sure to sync your local `main` branch before starting new work.

```bash
$ git checkout main
$ git pull origin main
```

</br>
</br>
</br>

# First Step

### Background

We love [Nest.js](https://nestjs.com/), but we felt that the Controller and Module in [Nest.js](https://nestjs.com/) are unnecessary for simple tasks.

### Getting Started

In this document, we will explore the **core principles** of Ezy API. To familiarize yourself with the essential components of an Ezy API application, you should build a basic CRUD application covering various areas at a basic level.

#### Language

Ezy API uses the [Python](https://www.python.org/) language.

In the future, we plan to support languages like [TypeScript](https://www.typescriptlang.org/) and [Java](https://java.com/).

#### Prerequisites

Make sure you have [Python](https://www.python.org/) (>= 3.6) installed on your operating system.

#### Setup

Setting up a new project with the [Ezy API CLI](#cli-overview) is very simple. If [pip](https://pypi.org/project/pip/) is installed, you can create a new Ezy API project in the OS terminal with the following command:

```bash
$ pip install ezyapi
$ ezy new project-name
```

A directory called `project-name` will be created along with a `main.py` and CLI configuration files. 

The basic structure of the project looks like this:
```
app_service.py
ezy.json
main.py
```

> **Tip**  
> 
> You can view these files [here](https://github.com/3x-haust/Python_Ezy_API/tree/main/example).

<br></br>

Here is a brief description of the core files:

| Filename       | Description |
|:--------------:|:----------:|
| `app_service.py` | Basic service file |
| `ezy.json`       | CLI command configuration file |
| `main.py`        | Entry point. Creates an Ezy API application instance using the core function `EzyAPI`. |

> You don't need to fully understand services and other components at this stage. Detailed explanations will follow in upcoming chapters!

<br><br/>

Let’s start with creating a simple `main.py` file. This file contains the main module that starts the application.

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

You can run the application with the following command in the OS terminal:

```bash
$ ezy run start
```

</br>
</br>
</br>

# Services

### What is a Service?

In Ezy API, a **Service** is the core component responsible for processing requests and performing business logic.  
It functions similarly to [Nest.js](https://nestjs.com)'s Controller and Service, but Ezy API is designed to allow you to build an API with just services in a much more concise and intuitive way.

### Service Structure

Services are created by inheriting the `EzyService` class.  
Here’s an example of a basic service:

> **Tip**  
> 
> You can generate a service using ```$ ezy g res user```

```python
# app_service.py
from ezyapi import EzyService

class AppService(EzyService):
    async def get_app(self) -> str:
        return "Hello, World!"
```

- By inheriting `EzyService`, you can define API endpoints as asynchronous functions within the service.
- The function name automatically becomes the API endpoint URL.
  - For example, the `get_user` function is automatically mapped to the `/user/` path with the `GET` method.
    - However, if the service name is `app`, it is mapped to the root path.
- Functions are defined as `async` to allow asynchronous processing.

### URL Mapping Rules

The function name in a service is automatically mapped to a URL endpoint.

| Function Name    | HTTP Method | URL          |
|:----------------:|:-----------:|:------------:|
| `get_user`       | GET         | `/user/`     |
| `list_users`     | GET         | `/user/`     |
| `create_user`    | POST        | `/user/`     |
| `update_user`    | PUT         | `/user/`     |
| `delete_user`    | DELETE      | `/user/`     |
| `edit_user`      | PATCH       | `/user/`     |

> **Tip**  
> 
> Methods like `get`, `update`, `delete`, `edit` can use path parameters like `by_id`, etc.  
> For example: `get_user_by_id` ➡️ `GET /user/{id}`

### Registering a Service

Services can be registered to the EzyAPI instance in `main.py`:

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

### Path Parameter Example

Ezy API automatically maps path parameters to the URL when you add `by_id`, `by_name`, etc., to a function name.

```python
# user_service.py
from ezyapi import EzyService

class UserService(EzyService):
    async def get_user_by_id(self, id: int) -> dict:
        return {"id": id, "name": "John Doe"}
```

- `get_user_by_id` ➡️ `GET /user/{id}` is automatically mapped.
- The `id` is used as a path parameter in the URL.

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

### Query Parameter Example

Query parameters can be received as query strings by defining `Optional` and default values for function arguments.

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
- You can pass `name` and `age` as query parameters.

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

### Decorator Example (@route)

You can manually specify the URL and method by using the `@route()` decorator on a service function.

```python
# user_service.py
from ezyapi import EzyService
from ezyapi.core import route

class UserService(EzyService):
    @route('get', '/name/{name}', description="Get user by name")
    async def get_user_by_name(self, name: str) -> dict:
        return {"name": name, "email": "example@example.com"}
```

- `@route('get', '/name/{name}')` ➡️ `GET /name/{name}` is mapped.
- The `description` is used for API documentation.

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

> **Tip**  
> 
> Using the `@route()` decorator overrides automatic mapping, allowing you to freely set the desired URL and HTTP method.

</br>
</br>
</br>

# CLI Overview
