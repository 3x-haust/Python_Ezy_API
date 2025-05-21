This README is the English version.  
[Click here for the Korean version.](./README.ko.md)

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
  - [Submit a Pull Request (PR)](#submit-a-pull-request-pr)
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
- [CLI Overview](#cli-overview)
    - [Installation](#installation)
    - [Commands](#commands)
    - [Examples](#examples)
      - [Create a New Project](#create-a-new-project)
      - [Generate a Resource](#generate-a-resource)
      - [Install Dependencies](#install-dependencies)
      - [Run Scripts](#run-scripts)
      - [Run Tests](#run-tests)
      - [Lint Code](#lint-code)
      - [View Information](#view-information)
      - [Initialize a Project](#initialize-a-project)
    - [Project Structure](#project-structure)

</br>
</br>
</br>

# How to Contribute

Anyone can freely contribute to Ezy API!  
Please follow the procedure below to participate comfortably.

## Fork the Project

Fork the project to work in your personal repository and then submit a PR.

## Create a Branch

When starting new work, please create a **branch**. Branches are typically written in the form of `feature/{feature-name}`.

```bash
# Move to the main branch and sync with the latest state
$ git checkout main
$ git pull origin main

# Create and move to a new branch
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
| `test/` | Add or modify test code | `test/user-service-test` |
| `chore/` | Build settings, package management, other miscellaneous tasks | `chore/update-deps`, `chore/ci-config` |

> **Tip**
> 
> Branch names should clearly reflect the content of your work.


## Work and Commit

After completing your work, please write commit messages according to the **commit conventions** below.

### Commit Message Convention

| Tag | Description |
|:---:|:---|
| `feat` | Add new features |
| `fix` | Fix bugs |
| `docs` | Modify documentation (README, comments, etc.) |
| `style` | Code formatting, spelling fixes, etc. that don't affect the code functionality |
| `refactor` | Code refactoring (improving internal logic without changing behavior) |
| `test` | Add or modify test code |
| `chore` | Build tasks, package manager configuration, maintenance work, etc. |

### Commit Examples
```bash
$ git commit -m "feat: Add user API"
$ git commit -m "fix: Fix incorrect router path"
$ git commit -m "docs: Add installation method to README"
```

## Push to Remote Repository

Push your branch to the remote repository.

```bash
$ git push origin feature/feature-name
```

## Submit a Pull Request (PR)

- Create a **Pull Request** on GitHub.
- Briefly explain what work you did in the PR description.
- Proceed with code review with team members.

## Merge

- After review and approval, **merge to the main branch**.
- After merging, always sync your `main` branch to the latest before starting other work.

```bash
$ git checkout main
$ git pull origin main
```

</br>
</br>
</br>

# First Steps

### Background

We like [Nest.js](https://nestjs.com/), but we thought that Nest.js's Controller, Module, etc. were unnecessary for simple tasks.

### Getting Started

In this document, we'll explore the **core principles** of Ezy API. To understand the essential components of an Ezy API application,
you need to build a basic CRUD application covering many areas at a fundamental level.

#### Language

Ezy API uses the [Python](https://www.python.org/) language.

In the future, we plan to support other languages such as [TypeScript](https://www.typescriptlang.org/) and [Java](https://java.com/).

#### Prerequisites

Make sure [Python](https://www.python.org/) (>= 3.11) is installed on your operating system.

#### Setup

Setting up a new project with [Ezy API CLI](#cli-overview) is very simple. If you have [pip](https://pypi.org/project/pip/) installed, you can create a new Ezy API project using the following command in your OS terminal:


```bash
$ pip install ezyapi
$ ezy new project-name
```

A `project-name` directory will be created, along with main.py and CLI configuration files.

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

The core files described above can be briefly explained as follows:

|Filename|Description|
|:---:|:---|
|`app_service.py`|Basic service file|
|`ezy.json`|CLI command configuration file|
|`main.py`|Entry file. Uses the core function `EzyAPI` to create an Ezy API application instance.|

> If you don't understand the services described above, that's okay. More detailed explanations will come in later chapters!

<br><br/>

Let's start by creating a simple main.py file. This file contains the main module that starts the application.

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

You can run the application using the following command in your OS terminal:
```bash
$ ezy run start
```

</br>
</br>
</br>

# Services

### What is a Service?

In Ezy API, a **Service** is a core component that handles requests and performs business logic.  
It plays a similar role to Controllers or Services in [Nest.js](https://nestjs.com), but Ezy API is designed to allow you to configure APIs with just services in a more concise and intuitive way.

### Service Structure

A service is created by inheriting from the `EzyService` class.  
Below is an example of a basic service:
> **Tip**
>
> You can create a service using ```$ ezy g res user```

```python
# app_service.py
from ezyapi import EzyService

class AppService(EzyService):
    async def get_app(self) -> str:
        return "Hello, World!"
```

- By inheriting from `EzyService`, you can define API endpoints as asynchronous functions within the service.
- The function name becomes the API endpoint URL.
  - For example, a function called `get_user` is automatically mapped to the `/user/` path with the `GET` method.
    - As an exception, if the service name is `app`, it's mapped to the root path.
- Functions can be defined with `async` to enable asynchronous processing.

### URL Mapping Rules

The function names of the service are automatically mapped to URL endpoints.

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
> The `get`, `update`, `delete`, `edit` methods can use `by_id` etc. to `use path parameters`
> Example: `get_user_by_id` ➡️ `GET /user/{id}`

### Service Registration

Services can be registered to the EzyAPI instance in `main.py`.

```python
# main.py
from ezyapi import EzyAPI
from ezyapi.database import DatabaseConfig
from app_service import AppService

if __name__ == "__main__":
    app.add_service(AppService)
    app.run(port=8000)
```

### Path Parameter Example

Ezy API automatically maps parameters to URL paths when you add `by_id`, `by_name`, etc. to the function name.

```python
# user_service.py
from ezyapi import EzyService

class UserService(EzyService):
    async def get_user_by_id(self, id: int) -> dict:
        return {"id": id, "name": "John Doe"}
```

- `get_user_by_id` ➡️ Automatically mapped to the `GET /user/{id}` path.
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
- You can pass `name` and `age` as query strings.

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

You can manually specify the URL and method by using the `@route()` decorator directly on service functions.

```python
# user_service.py
from ezyapi import EzyService
from ezyapi.core import route

class UserService(EzyService):
    @route('get', '/name/{name}', description="Get user by name")
    async def get_user_by_name(self, name: str) -> dict:
        return {"name": name, "email": "example@example.com"}
```

- `@route('get', '/name/{name}')` ➡️ Sets the path to `GET /name/{name}`.
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
> Using the `@route()` decorator allows you to override automatic mapping and freely set the desired URL and HTTP method.

</br>
</br>
</br>

# CLI Overview

Ezy CLI is a command-line interface tool designed to simplify Ezy API project management. It provides various commands to easily perform project creation, building, testing, and execution.

### Installation

Ezy CLI can be installed using pip:

```bash
$ pip install ezyapi
```

> **Note**
>
> Make sure Python 3.11 or higher is installed on your system.

### Commands

Ezy CLI supports the following commands:

| Command | Description |
|:---|:---|
|`new <project_name>`|Creates a new Ezy API project with the specified name.|
|`generate <type> <name>` or `g <type> <name>`|Generates a component of the specified type (e.g., 'res' for resource) and name.|
|`install [packages...]` or `install -r <requirements.txt>`|Installs dependencies in the ezy_modules directory. You can specify packages directly or use a requirements.txt file.|
|`run <script>`|Runs scripts defined in ezy.json (e.g., 'dev' or 'start').|
|`test`|Runs tests in the 'test' directory using pytest.|
|`lint`|Checks code style using flake8.|
|`info`|Displays CLI version, Python version, platform, and current directory information.|
|`init [project_name]`|Initializes a new Ezy project in the current directory. If no project name is specified, the current directory name is used.|

### Examples

#### Create a New Project

```bash
$ ezy new my_project
```

Creates the basic structure of an Ezy API project in a directory named `my_project`.

#### Generate a Resource

```bash
$ ezy generate res user
```

Creates a resource named "user", optionally including CRUD operations.

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

Assuming scripts are defined in ezy.json, for example:

```json
{
  "scripts": {
    "start": "python3 main.py",
    "dev": "python3 main.py --dev"
  }
}
```

You can execute them as follows:

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

#### Lint Code

To check for code style issues:

```bash
$ ezy lint
```

> **Note**
> 
> flake8 must be installed.

#### View Information

To display CLI and system information:

```bash
$ ezy info
```

#### Initialize a Project

To initialize a new Ezy project in the current directory:

```bash
$ ezy init
```

### Project Structure

When you create a new project with the `ezy new <project_name>` command, the following structure is created:

```
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

* `ezy.json`: Project settings (including dependencies and scripts).
* `main.py`: Application entry point.
* `app_service.py`: Example service.
* `test/`: Directory for test files.
* `ezy_modules/`: Directory for project-specific dependencies.
* `.gitignore`: Git ignore file.

When you generate a resource with the `ezy generate res <name>` command, the following structure is created:

```
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

A test file is also created at `test/test_<name>_service.py`.

> **Note**
> 
> * The CLI uses color codes to enhance readability in terminals that support ANSI colors.
> * The `test` command requires pytest to be installed. It is included in the default dependencies of new projects.
> * The `lint` command requires flake8. You may need to install it separately.
> * The `update` command currently only simulates updates without actually performing them.