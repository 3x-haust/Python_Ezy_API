This README is the English version.  
[한국어 버전은 여기를 클릭하세요.](./README.ko.md)

![Contributors](https://img.shields.io/github/contributors/3x-haust/Python_Ezy_API?style=flat)
![Forks](https://img.shields.io/github/forks/3x-haust/Python_Ezy_API?style=social?style=flat)
[![Stars](https://img.shields.io/github/stars/3x-haust/Python_Ezy_API?style=flat&logo=GitHub&color=yellow)](https://github.com/3x-haust/Python_Ezy_API/stargazers)
![License](https://img.shields.io/github/license/3x-haust/Python_Ezy_API?style=flat)
[![PyPI](https://img.shields.io/pypi/v/ezyapi?logo=PyPI?style=flat)](https://pypi.org/project/ezyapi/)

</br>

# Table of Contents
- [Table of Contents](#table-of-contents)
- [How to Contribute](#how-to-contribute)
  - [Fork the Project](#fork-the-project)
  - [Create a Branch](#create-a-branch)
    - [Branch Naming Convention](#branch-naming-convention)
  - [Work and Commit](#work-and-commit)
    - [Commit Message Convention](#commit-message-convention)
    - [Commit Examples](#commit-examples)
  - [Push to Remote Repository](#push-to-remote-repository)
  - [Create Pull Request (PR)](#create-pull-request-pr)
  - [Merge](#merge)
- [First Steps](#first-steps)
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
    - [Service Registration](#service-registration)
    - [Path Parameter Example](#path-parameter-example)
    - [Query Parameter Example](#query-parameter-example)
    - [Decorator Example (@route)](#decorator-example-route)
- [Database and Entities](#database-and-entities)
    - [Database Configuration](#database-configuration)
    - [Entity Definition](#entity-definition)
      - [Basic Entity (Simple Method)](#basic-entity-simple-method)
      - [Advanced Entity with Annotations](#advanced-entity-with-annotations)
      - [Column Annotation Types](#column-annotation-types)
      - [Column Options](#column-options)
      - [Various Primary Key Examples](#various-primary-key-examples)
    - [Entity Relations](#entity-relations)
      - [Relation Definition](#relation-definition)
      - [Relation Types](#relation-types)
      - [Loading Related Data](#loading-related-data)
      - [Relation Loading Examples](#relation-loading-examples)
- [CLI Overview](#cli-overview)
    - [Installation](#installation)
    - [Commands](#commands)
    - [Examples](#examples)
      - [Create New Project](#create-new-project)
      - [Generate Resource](#generate-resource)
      - [Install Dependencies](#install-dependencies)
      - [Run Scripts](#run-scripts)
      - [Run Tests](#run-tests)
      - [Code Linting](#code-linting)
      - [Check Information](#check-information)
      - [Initialize Project](#initialize-project)
    - [Project Structure](#project-structure)

</br>
</br>
</br>

# How to Contribute

Anyone can freely contribute to Ezy API!  
Please follow the procedures below to participate comfortably.

## Fork the Project

Please fork the project to work in your personal repository and then create a PR.

## Create a Branch

When starting new work, please create a **branch**. Branches are usually written in the format `feature/{feature-name}`.

```bash
# Move to main branch and sync to latest state
$ git checkout main
$ git pull origin main

# Create and switch to new branch
$ git checkout -b feature/feature-name
```

### Branch Naming Convention

Please write branch names according to the nature of your work.

| Type | Description | Example |
|:---:|:---|:---|
| `feature/` | New feature development | `feature/login-api`, `feature/add-user-api` |
| `fix/` | Bug fixes | `fix/login-bug`, `fix/routing-error` |
| `docs/` | Documentation work (README, comments, etc.) | `docs/update-readme`, `docs/api-docs` |
| `refactor/` | Code refactoring | `refactor/login-service`, `refactor/db-helper` |
| `test/` | Adding and modifying test code | `test/user-service-test` |
| `chore/` | Build configuration, package management, other maintenance | `chore/update-deps`, `chore/ci-config` |

> **Tip**
> 
> It's good to have branch names clearly indicate the work content.

## Work and Commit

After completing your work, write commit messages referring to the **commit convention** below.

### Commit Message Convention

| Tag | Description |
|:---:|:---|
| `feat` | Add new feature |
| `fix` | Bug fix |
| `docs` | Documentation modification (README, comments, etc.) |
| `style` | Code formatting, spelling corrections, etc. - changes that don't affect code behavior |
| `refactor` | Code refactoring (improving internal logic without behavioral changes) |
| `test` | Adding and modifying test code |
| `chore` | Build tasks, package manager configuration, maintenance work, etc. |

### Commit Examples
```bash
$ git commit -m "feat: add user API"
$ git commit -m "fix: correct wrong router path"
$ git commit -m "docs: add installation instructions to README"
```

## Push to Remote Repository

Push your created branch to the remote repository.

```bash
$ git push origin feature/feature-name
```

## Create Pull Request (PR)

- Create a **Pull Request** on GitHub.
- Write a brief description of what work you've done in the PR description.
- Then proceed with code review with team members.

## Merge

- After review is complete and approval is received, **merge to main branch**.
- After merging, always sync the `main` branch to the latest before other work.

```bash
$ git checkout main
$ git pull origin main
```

</br>
</br>
</br>

# First Steps

### Background

We love [Nest.js](https://nestjs.com/), but we thought that [Nest.js](https://nestjs.com/)'s Controllers, Modules, etc. are unnecessary for simple tasks.

### Getting Started

This document covers the **core principles** of Ezy API. To familiarize yourself with the essential components of an Ezy API application, you need to cover many areas at a basic level and build a basic CRUD application.

#### Language

Ezy API uses the [Python](https://www.python.org/) language.

In the future, we plan to support usage in languages like [TypeScript](https://www.typescriptlang.org/), [Java](https://java.com/), etc.

#### Prerequisites

Make sure [Python](https://www.python.org/) (>= 3.11) is installed on your operating system.

#### Setup

Setting up a new project with [Ezy API CLI](#cli-overview) is very simple. If you have [pip](https://pypi.org/project/pip/) installed, you can create a new Ezy API project using the following commands in your OS terminal.

```bash
$ pip install ezyapi
$ ezy new project-name
```

The `project-name` directory is created, and main.py and cli configuration files are generated.

The basic structure of the project is as follows:
```
app_service.py
ezy.json
main.py
```
> **Tip**
> 
> The above files can be found [here](https://github.com/3x-haust/Python_Ezy_API/tree/main/example).

<br></br>

A brief explanation of the core files above:

|File Name|Description|
|:---:|:---|
|`app_service.py`|Basic service file|
|`ezy.json`|CLI command configuration file|
|`main.py`|Entry file. Creates an Ezy API application instance using the core function `EzyAPI`.|

> Don't worry if you don't understand the services mentioned above. Detailed explanations will come in later chapters!

<br><br/>

Let's start by creating the main.py file. This file contains the main module that starts the application.

```python
# main.py
from ezyapi import EzyAPI
from ezyapi.database import DatabaseConfig
from user.user_service import UserService
from app_service import AppService

app = EzyAPI()

if __name__ == "__main__":
    app.run(port=8000)
```

> **Tip**
>>
> During development, you can use the `reload=True` option to automatically restart the server when code changes.

### Running the Application

You can run the application with the following command in your OS terminal:
```bash
$ ezy run start
```

</br>
</br>
</br>

# Services

### What is a Service?

In Ezy API, a **Service** is a core component that handles requests and performs business logic.  
It serves a similar role to Controllers or Services in [Nest.js](https://nestjs.com), but Ezy API is designed so that services alone can sufficiently compose APIs in a more concise and intuitive way.

### Service Structure

Services are created by inheriting from the `EzyService` class.  
Below is an example of a basic service:
> **Tip**
>
> Services can be generated using ```$ ezy g res user```

```python
# app_service.py
from ezyapi import EzyService

class AppService(EzyService):
    async def get_app(self) -> str:
        return "Hello, World!"
```

- By inheriting from `EzyService`, you can define API endpoints as asynchronous functions within the service.
- Function names become the API endpoint URLs.
  - For example, a function called `get_user` is automatically mapped to the `/user/` path with the `GET` method.
    - However, as an exception, when the service name is `app`, it maps to the root path.
- Functions are defined as `async` to enable asynchronous processing.

### URL Mapping Rules

Service function names are automatically mapped to URL endpoints.

| Function Name | HTTP Method | URL |
|:---:|:---:|:---|
|`get_user`|GET|`/user/`|
|`list_users`|GET|`/user/`|
|`create_user`|POST|`/user/`|
|`update_user`|PUT|`/user/`|
|`delete_user`|DELETE|`/user/`|
|`edit_user`|PATCH|`/user/`|

> **Tip**
>
> Methods like `get`, `update`, `delete`, `edit` can use path parameters with `by_id`, etc.  
> Example: `get_user_by_id` ➡️ `GET /user/{id}`

### Service Registration

Services can be registered with the EzyAPI instance in `main.py`.

```python
# main.py
from ezyapi import EzyAPI
from ezyapi.database import DatabaseConfig
from app_service import AppService

app = EzyAPI()
app.add_service(AppService)

if __name__ == "__main__":
    app.run(port=8000)
```

### Path Parameter Example

Ezy API automatically maps parameters to URL paths when you add `by_id`, `by_name`, etc. to function names.

```python
# user_service.py
from ezyapi import EzyService

class UserService(EzyService):
    async def get_user_by_id(self, id: int) -> dict:
        return {"id": id, "name": "John Doe"}
```

- `get_user_by_id` ➡️ Automatically mapped to `GET /user/{id}` path.
- `id` is used as a `path parameter` in the URL path.

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

Query parameters can be received as query strings by defining `Optional` and default values in function arguments.

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
- You can pass `name`, `age` as query strings.

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

### Decorator Example (@route)

You can manually specify URLs and methods by using the `@route()` decorator directly on service functions.

```python
# user_service.py
from ezyapi import EzyService, route

class UserService(EzyService):
    @route('get', '/name/{name}', description="Get user by name")
    async def get_user_by_name(self, name: str) -> dict:
        return {"name": name, "email": "example@example.com"}
```

- `@route('get', '/name/{name}')` ➡️ Set to `GET /name/{name}` path.
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

> **Tip**
>
> Using the `@route()` decorator allows you to override automatic mapping and freely set desired URLs and HTTP methods.

</br>
</br>
</br>

# Database and Entities

### Database Configuration

Ezy API supports various database types including SQLite, MySQL, PostgreSQL, MongoDB, etc.

```python
# main.py
from ezyapi import EzyAPI
from ezyapi.database import DatabaseConfig
from user.user_service import UserService

if __name__ == "__main__":
    app = EzyAPI()
    
    # SQLite configuration
    db_config = DatabaseConfig(
        db_type="sqlite",
        connection_params={
            "dbname": "./app.db"
        }
    )
    
    # Or MySQL configuration
    # db_config = DatabaseConfig(
    #     db_type="mysql",
    #     connection_params={
    #         "host": "localhost",
    #         "port": 3306,
    #         "user": "root",
    #         "password": "password",
    #         "dbname": "myapp"
    #     }
    # )
    
    app.configure_database(db_config)
    app.add_service(UserService)
    app.run(port=8000)
```

### Entity Definition

Entities are defined by inheriting from `EzyEntityBase`. TypeORM-style annotations can be used for advanced column configuration.

#### Basic Entity (Simple Method)

```python
# user/entity/user_entity.py
from ezyapi import EzyEntityBase

class UserEntity(EzyEntityBase):
    def __init__(self, id: int = None, name: str = "", email: str = ""):
        self.id = id
        self.name = name
        self.email = email

# This way, id automatically becomes PrimaryGeneratedColumn
```

#### Advanced Entity with Annotations

Annotations can be used for more granular control over database columns:

```python
# user/entity/user_entity.py
from typing import Annotated
from ezyapi import EzyEntityBase, PrimaryGeneratedColumn, Column

class UserEntity(EzyEntityBase):
    def __init__(self, email: str = ""):
        self.email = email
    
    # Use annotation to explicitly specify PrimaryGeneratedColumn
    id: Annotated[int, PrimaryGeneratedColumn()] = None
    
    # Add annotations only to fields that need special configuration
    name: Annotated[str, Column(nullable=False, column_type="VARCHAR(100)")] = ""
```

#### Column Annotation Types

| Annotation | Description | Example |
|:---|:---|:---|
| `PrimaryColumn()` | Custom primary key (user-specified value) | `id: Annotated[str, PrimaryColumn(column_type="VARCHAR(50)")] = None` |
| `PrimaryGeneratedColumn()` | Auto-increment primary key | `id: Annotated[int, PrimaryGeneratedColumn(column_type="BIGINT")] = None` |
| `Column()` | Regular column with options | `name: Annotated[str, Column(nullable=False, unique=True)] = ""` |

#### Column Options

- `column_type`: Specify database column type (e.g., "VARCHAR(100)", "TEXT", "BIGINT")
- `nullable`: Whether the column allows NULL (default: True)
- `unique`: Whether to apply unique constraint to the column (default: False)
- `auto_increment`: Whether the column auto-increments (Column default: False, PrimaryGeneratedColumn: True)

#### Various Primary Key Examples

```python
# Basic auto-increment primary key (explicit annotation)
class TodoEntity(EzyEntityBase):
    def __init__(self, content: str = "", completed: bool = False):
        self.content = content
        self.completed = completed

    id: Annotated[int, PrimaryGeneratedColumn()] = None

# String primary key
class ProductEntity(EzyEntityBase):
    def __init__(self, name: str = "", price: float = 0.0):
        self.name = name
        self.price = price
        
    product_code: Annotated[str, PrimaryColumn(column_type="VARCHAR(20)")] = None

# Custom auto-increment primary key
class OrderEntity(EzyEntityBase):
    def __init__(self, user_id: int = 0, total_amount: float = 0.0):
        self.user_id = user_id
        self.total_amount = total_amount
        
    order_id: Annotated[int, PrimaryGeneratedColumn(column_type="BIGINT")] = None
```

> **Note**
>
> - Annotations are **optional** - only add them to fields that need special database configuration
> - Fields without annotations use default behavior (regular columns)
> - If there's an `id` parameter in the `__init__` method, it automatically becomes an auto-increment primary key

### Entity Relations

Ezy API supports TypeORM-style entity relations and can define OneToMany and ManyToOne relationships. You can define relationships between entities and efficiently load related data.

#### Relation Definition

```python
# user/entity/user_entity.py
from typing import List
from ezyapi import EzyEntityBase, OneToMany, ManyToOne

class UserEntity(EzyEntityBase):
    def __init__(self, id: int = None, name: str = "", email: str = ""):
        self.id = id
        self.name = name
        self.email = email
    
    # OneToMany relation: One user can have multiple posts
    posts: List['PostEntity'] = OneToMany('PostEntity', 'user_id')

class PostEntity(EzyEntityBase):
    def __init__(self, id: int = None, title: str = "", content: str = "", user_id: int = None):
        self.id = id
        self.title = title
        self.content = content
        self.user_id = user_id
    
    # ManyToOne relation: Multiple posts can belong to one user
    user: 'UserEntity' = ManyToOne('UserEntity', 'user_id')
```

#### Relation Types

| Relation | Description | Example |
|:---|:---|:---|
| `OneToMany(target_entity, mapped_by)` | One entity has multiple related entities | `posts: List['PostEntity'] = OneToMany('PostEntity', 'user_id')` |
| `ManyToOne(target_entity, foreign_key)` | Multiple entities belong to one entity | `user: UserEntity = ManyToOne(UserEntity, 'user_id')` |

#### Loading Related Data

You can use the `relations` parameter in repository methods to load related entities:

```python
# user_service.py
from ezyapi import EzyService
from ezyapi.database import DatabaseConfig
from user.entity.user_entity import UserEntity

class UserService(EzyService):
    def __init__(self):
        db_config = DatabaseConfig.get_instance()
        self.user_repository = db_config.get_repository(UserEntity)
    
    async def get_users_with_posts(self):
        # Load users with their posts
        users = await self.user_repository.find(relations=["posts"])
        return users
    
    async def get_user_with_posts_by_id(self, user_id: int):
        # Load specific user with their posts
        user = await self.user_repository.find_one(
            where={"id": user_id}, 
            relations=["posts"]
        )
        return user

# post_service.py
from post.entity.post_entity import PostEntity

class PostService(EzyService):
    def __init__(self):
        db_config = DatabaseConfig.get_instance()
        self.post_repository = db_config.get_repository(PostEntity)
    
    async def get_posts_with_users(self):
        # Load posts with associated users
        posts = await self.post_repository.find(relations=["user"])
        return posts
```

#### Relation Loading Examples

```python
# Load multiple relations
users = await user_repository.find(relations=["posts", "profile", "comments"])

# Load specific user with relations
user = await user_repository.find_one(
    where={"id": 1}, 
    relations=["posts"]
)

# The loaded user object has the posts attribute populated
print(user.posts)  # List of PostEntity objects
```

</br>
</br>
</br>

# CLI Overview

Ezy CLI is a command-line interface tool designed to simplify Ezy API project management. It provides various commands to easily perform project creation, building, testing, running, and more.

### Installation

Ezy CLI can be installed using pip:

```bash
$ pip install ezyapi
```

> **Note**
>
> Make sure you have Python 3.11 or higher installed on your system.

### Commands

Ezy CLI supports the following commands:

| Command | Description |
|:---|:---|
|`new <project_name>`|Creates a new Ezy API project with the specified name.|
|`generate <type> <name>` or `g <type> <name>`|Generates a component with the specified type (e.g., 'res' for resource) and name.|
|`install [packages...]` or `install -r <requirements.txt>`|Installs dependencies in the ezy_modules directory. You can specify packages directly or use a requirements.txt file.|
|`run <script>`|Runs a script defined in ezy.json (e.g., 'dev' or 'start').|
|`test`|Runs tests in the 'test' directory using pytest.|
|`lint`|Checks code style using flake8.|
|`info`|Displays CLI version, Python version, platform, and current directory information.|
|`init [project_name]`|Initializes a new Ezy project in the current directory. If no project name is specified, the current directory name is used.|

### Examples

#### Create New Project

```bash
$ ezy new my_project
```

Creates the basic structure of an Ezy API project in a directory named `my_project`.

#### Generate Resource

```bash
$ ezy generate res user
```

Generates a resource named "user", optionally including CRUD operations.

#### Install Dependencies

To install dependencies listed in ezy.json:

```bash
$ ezy install
```

To install specific packages:

```bash
$ ezy install requests numpy
```

To install from a requirements.txt file:

```bash
$ ezy install -r requirements.txt
```

#### Run Scripts

Assuming you have scripts defined in ezy.json, for example:

```json
{
  "scripts": {
    "start": "python3 main.py",
    "dev": "python3 main.py --dev"
  }
}
```

You can run them like this:

```bash
$ ezy run start
```

#### Run Tests

To run tests:

```bash
$ ezy test
```

> **Note**
>
> pytest must be installed.

#### Code Linting

To check for code style issues:

```bash
$ ezy lint
```

> **Note**
>
> flake8 must be installed.

#### Check Information

To display CLI and system information:

```bash
$ ezy info
```

#### Initialize Project

To initialize a new Ezy project in the current directory:

```bash
$ ezy init
```

### Project Structure

When you create a new project with the `ezy new <project_name>` command, the following structure is created:

```text
project_name/
├── ezy.json
├── main.py
├── app_service.py
├── test/
│   └── (test files)
├── ezy_modules/
│   └── (installed dependencies)
└── .gitignore
```

- `ezy.json`: Project configuration (including dependencies and scripts).
- `main.py`: Application entry point.
- `app_service.py`: Example service.
- `test/`: Directory for test files.
- `ezy_modules/`: Directory for project-specific dependencies.
- `.gitignore`: Git ignore file.

When you generate a resource with the `ezy generate res <name>` command, the following structure is created:

```text
<name>/
├── __init__.py
├── dto/
│   ├── __init__.py
│   ├── <name>_create_dto.py
│   └── <name>_update_dto.py
├── entity/
│   ├── __init__.py
│   └── <name>_entity.py
└── <name>_service.py
```

Additionally, a test file is created at `test/test_<name>_service.py`.

> **Note**
>
> - The CLI uses color codes for better readability in terminals that support ANSI colors.
> - The `test` command requires pytest to be installed. It's included in the default dependencies of new projects.
> - The `lint` command requires flake8. You may need to install it separately.
> - The `update` command currently only simulates updates and doesn't perform actual updates.