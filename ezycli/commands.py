#!/usr/bin/env python3
import argparse
import os
import sys
import subprocess
import json
import py_compile

CLI_VERSION = "0.1.0"

def new_project(project_name):
    project_path = os.path.join(os.getcwd(), project_name)
    if os.path.exists(project_path):
        print(f"Error: Project '{project_name}' already exists.", file=sys.stderr)
        sys.exit(1)
    os.makedirs(project_path)
    os.makedirs(os.path.join(project_path, "test"))
    os.makedirs(os.path.join(project_path, "ezy_modules"))
    with open(os.path.join(project_path, ".gitignore"), "w", encoding="utf-8") as f:
        f.write(""".venv
ezy_modules/
__pycache__/
*.pyc
.env
""")
    ezy_json_content = {
        "scripts": {
            "start": "python3 main.py",
            "dev": "python3 main.py --dev"
        },
        "dependencies": {
            "ezyapi": "latest",
            "fastapi": ">=0.68.0",
            "uvicorn": ">=0.15.0",
            "pydantic": ">=1.8.0"
        }
    }
    with open(os.path.join(project_path, "ezy.json"), "w", encoding="utf-8") as f:
        json.dump(ezy_json_content, f, indent=2)
    with open(os.path.join(project_path, "pyproject.toml"), "w", encoding="utf-8") as f:
        f.write(f"""[project]
name = "{project_name}"
version = "0.1.0"
description = "Ezy API project"
authors = [{{ name="Your Name"}}]
dependencies = []

[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"
""")
    with open(os.path.join(project_path, "requirements.txt"), "w", encoding="utf-8") as f:
        f.write("""# External dependency packages
ezy-api
fastapi>=0.68.0
uvicorn>=0.15.0
pydantic>=1.8.0
pytest>=6.2.5
flake8>=3.9.0
""")
    main_py_content = """from ezyapi import EzyAPI
from ezyapi.database import DatabaseConfig
from app_service import AppService

if __name__ == "__main__":
    app = EzyAPI()
    app.add_service(AppService)
    app.run(port=8000)
"""
    with open(os.path.join(project_path, "main.py"), "w", encoding="utf-8") as f:
        f.write(main_py_content)
    app_service_content = """from ezyapi import EzyService

class AppService(EzyService):
    async def get_app(self) -> str:
        return "Hello, World!"
"""
    with open(os.path.join(project_path, "app_service.py"), "w", encoding="utf-8") as f:
        f.write(app_service_content)
    print(f"New Ezy API project '{project_name}' created at: {project_path}")
    print("Next steps:")
    print(f"  cd {project_name} && python -m venv .venv && .venv\\Scripts\\activate && pip install -r requirements.txt")
    print("Run the server with: ezy run start")

def generate_resource(name):
    try:
        with open("ezy.json", "r", encoding="utf-8") as f:
            _ = json.load(f)
    except Exception:
        pass

    base_dir = os.getcwd()
    name_lower = name.lower()
    Name = name.capitalize()
    resource_dir = os.path.join(base_dir, name_lower)
    if os.path.exists(resource_dir):
        print(f"Error: Resource folder already exists: {resource_dir}", file=sys.stderr)
        sys.exit(1)
    os.makedirs(resource_dir)
    with open(os.path.join(resource_dir, "__init__.py"), "w", encoding="utf-8") as f:
        f.write("")
    dto_dir = os.path.join(resource_dir, "dto")
    os.makedirs(dto_dir)
    with open(os.path.join(dto_dir, "__init__.py"), "w", encoding="utf-8") as f:
        f.write("")
    entity_dir = os.path.join(resource_dir, "entity")
    os.makedirs(entity_dir)
    with open(os.path.join(entity_dir, "__init__.py"), "w", encoding="utf-8") as f:
        f.write("")
    create_dto_path = os.path.join(dto_dir, f"{name_lower}_create_dto.py")
    with open(create_dto_path, "w", encoding="utf-8") as f:
        f.write(f"""from pydantic import BaseModel

class {Name}CreateDTO(BaseModel):
    name: str
    email: str
    age: int = None
""")
    response_dto_path = os.path.join(dto_dir, f"{name_lower}_response_dto.py")
    with open(response_dto_path, "w", encoding="utf-8") as f:
        f.write(f"""from pydantic import BaseModel

class {Name}ResponseDTO(BaseModel):
    id: int
    name: str
    email: str
    age: int = None
""")
    entity_path = os.path.join(entity_dir, f"{name_lower}_entity.py")
    with open(entity_path, "w", encoding="utf-8") as f:
        f.write(f"""from ezyapi.database import EzyEntityBase

class {Name}Entity(EzyEntityBase):
    def __init__(self, id: int = None, name: str = "", email: str = "", age: int = None):
        self.id = id
        self.name = name
        self.email = email
        self.age = age
""")
    service_path = os.path.join(resource_dir, f"{name_lower}_service.py")
    service_code = f"""from ezyapi.core import route
from fastapi import HTTPException
from typing import List

from {name_lower}.dto.{name_lower}_response_dto import {Name}ResponseDTO
from {name_lower}.dto.{name_lower}_create_dto import {Name}CreateDTO
from {name_lower}.entity import {Name}Entity

from ezyapi import EzyService

class {Name}Service(EzyService):
    @route('get', '/{name_lower}/{{name}}', description="Get {Name} by name")
    async def get_{name_lower}_by_name(self, name: str) -> {Name}ResponseDTO:
        user = await self.repository.find_one(where={{"name": name}})
        if not user:
            raise HTTPException(status_code=404, detail="{Name} not found")
        return {Name}ResponseDTO(id=user.id, name=user.name, email=user.email, age=user.age)

    async def get_{name_lower}_by_id(self, id: int) -> {Name}ResponseDTO:
        user = await self.repository.find_one(where={{"id": id}})
        if not user:
            raise HTTPException(status_code=404, detail="{Name} not found")
        return {Name}ResponseDTO(id=user.id, name=user.name, email=user.email, age=user.age)
    
    async def list_{name_lower}s(self) -> List[{Name}ResponseDTO]:
        users = await self.repository.find()
        return [
            {Name}ResponseDTO(id=user.id, name=user.name, email=user.email, age=user.age)
            for user in users
        ]
    
    async def create_{name_lower}(self, data: {Name}CreateDTO) -> {Name}ResponseDTO:
        new_user = {Name}Entity(name=data.name, email=data.email, age=data.age)
        saved_user = await self.repository.save(new_user)
        return {Name}ResponseDTO(id=saved_user.id, name=saved_user.name, email=saved_user.email, age=saved_user.age)
    
    async def update_{name_lower}_by_id(self, id: int, data: {Name}CreateDTO) -> {Name}ResponseDTO:
        user = await self.repository.find_one(where={{"id": id}})
        if not user:
            raise HTTPException(status_code=404, detail="{Name} not found")
        user.name = data.name
        user.email = data.email
        user.age = data.age
        updated_user = await self.repository.save(user)
        return {Name}ResponseDTO(id=updated_user.id, name=updated_user.name, email=updated_user.email, age=updated_user.age)
    
    async def delete_{name_lower}_by_id(self, id: int) -> dict:
        success = await self.repository.delete(id)
        if not success:
            raise HTTPException(status_code=404, detail="{Name} not found")
        return {{"message": "{Name} deleted successfully"}}
"""
    with open(service_path, "w", encoding="utf-8") as f:
        f.write(service_code)
    print(f"Resource '{name}' created at: {resource_dir}")

def generate_component(component_type, name):
    if component_type == "res":
        generate_resource(name)
    else:
        print(f"Error: Unsupported type '{component_type}' (currently only 'res' is supported)", file=sys.stderr)
        sys.exit(1)

def generate_all_or_single(args):
    if not args.args or len(args.args) == 0:
        print("Component Generation Guide:")
        print("  Example: ezy g res user")
        print("    - 'res' indicates resource generation and 'user' is the component name.")
        print("  Supported types: res")
        sys.exit(0)
    elif len(args.args) == 2:
        component_type = args.args[0]
        name = args.args[1]
        generate_component(component_type, name)
    else:
        print("Error: Incorrect number of arguments. Example: ezy g res user", file=sys.stderr)
        sys.exit(1)

def build_project():
    base_dir = os.getcwd()
    errors = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                try:
                    py_compile.compile(path, doraise=True)
                except py_compile.PyCompileError as e:
                    errors.append(f"Syntax error: {path}\n  {e.msg}")
    if errors:
        print("Build failed:")
        for err in errors:
            print(err)
        sys.exit(1)
    print("Build completed successfully.")

def serve_project():
    main_py = os.path.join(os.getcwd(), "main.py")
    if not os.path.exists(main_py):
        print("Error: main.py does not exist.", file=sys.stderr)
        sys.exit(1)
    try:
        subprocess.run([sys.executable, main_py])
    except KeyboardInterrupt:
        print("\nServer stopped.")

def test_project():
    test_dir = os.path.join(os.getcwd(), "test")
    if not os.path.exists(test_dir):
        print("Error: 'test' folder does not exist.", file=sys.stderr)
        sys.exit(1)
    try:
        subprocess.run(["pytest", test_dir], check=True)
    except FileNotFoundError:
        print("Error: pytest is not installed. Install it via 'pip install pytest'.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("Error: Issues encountered during testing.", file=sys.stderr)
        sys.exit(1)

def lint_project():
    try:
        subprocess.run(["flake8", "."], check=True)
        print("Linting completed successfully.")
    except FileNotFoundError:
        print("Error: flake8 is not installed. Install it via 'pip install flake8'.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("Error: Linting issues detected.", file=sys.stderr)
        sys.exit(1)

def info_project():
    print(f"Ezy CLI Version: {CLI_VERSION}")
    print(f"Python Version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Current Directory: {os.getcwd()}")

def update_cli():
    print(f"Ezy CLI ({CLI_VERSION}) is up-to-date.")

def install_dependencies(args):
    config_path = os.path.join(os.getcwd(), "ezy.json")
    if not os.path.exists(config_path):
        print("Error: ezy.json not found. Are you in a project directory?", file=sys.stderr)
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    # 기존 dependencies 불러오기
    dependencies = config.get("dependencies", {})

    # 패키지 인자가 전달되었으면, 해당 패키지만 추가 및 설치
    if args.packages:
        packages_to_install = {}
        for pkg in args.packages:
            if "==" in pkg:
                pkg_name, pkg_version = pkg.split("==", 1)
                packages_to_install[pkg_name] = f"=={pkg_version}"
            else:
                packages_to_install[pkg] = "latest"
        # 새로 추가된 패키지를 config의 dependencies에 업데이트
        for pkg, ver in packages_to_install.items():
            dependencies[pkg] = ver
        config["dependencies"] = dependencies
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    else:
        # 인자가 없으면 전체 dependencies를 설치할 대상 패키지로 지정
        packages_to_install = dependencies

    if not packages_to_install:
        print("No dependencies to install.")
        return

    modules_path = os.path.join(os.getcwd(), "ezy_modules")
    if not os.path.exists(modules_path):
        os.makedirs(modules_path)
    print("Installing dependencies into ezy_modules...")
    for pkg, version in packages_to_install.items():
        pkg_spec = pkg if version == "latest" else f"{pkg}{version}"
        print(f"Installing {pkg_spec} ...")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "--target", modules_path, pkg_spec])
        if result.returncode != 0:
            print(f"Failed to install {pkg_spec}.", file=sys.stderr)
            sys.exit(1)
    print("Dependencies installed successfully.")

def run_script(args):
    config_path = os.path.join(os.getcwd(), "ezy.json")
    if not os.path.exists(config_path):
        print("Error: ezy.json not found. Are you in a project directory?", file=sys.stderr)
        sys.exit(1)
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    scripts = config.get("scripts", {})
    if not args.script:
        print("Error: No script name provided. Usage: ezy run <script>", file=sys.stderr)
        sys.exit(1)
    script_cmd = scripts.get(args.script)
    if not script_cmd:
        print(f"Error: Script '{args.script}' not found in ezy.json.", file=sys.stderr)
        sys.exit(1)
    print(f"Running script '{args.script}': {script_cmd}")
    
    # ezy_modules 폴더를 PYTHONPATH에 추가하여, 해당 폴더에 설치된 패키지들을 사용할 수 있게 합니다.
    modules_path = os.path.join(os.getcwd(), "ezy_modules")
    current_pythonpath = os.environ.get("PYTHONPATH", "")
    new_pythonpath = modules_path + os.pathsep + current_pythonpath if current_pythonpath else modules_path
    env = os.environ.copy()
    env["PYTHONPATH"] = new_pythonpath

    subprocess.run(script_cmd, shell=True, env=env)

def main():
    parser = argparse.ArgumentParser(prog="ezy", description="Ezy CLI - Ezy API project management tool")
    subparsers = parser.add_subparsers(dest="command")
    
    new_parser = subparsers.add_parser("new", help="Create a new Ezy API project")
    new_parser.add_argument("project_name", help="Name of the project")
    new_parser.set_defaults(func=lambda args: new_project(args.project_name))
    
    generate_parser = subparsers.add_parser("generate", aliases=["g"], help="Generate a component (e.g., 'ezy g res user')")
    generate_parser.add_argument("args", nargs="*", help="Component type and name (e.g., 'res user')")
    generate_parser.set_defaults(func=lambda args: generate_all_or_single(args))
    
    install_parser = subparsers.add_parser("install", help="Install dependencies into ezy_modules or add new packages")
    install_parser.add_argument("packages", nargs="*", help="Optional: package names to install (e.g., opencv or opencv==4.5.3)")
    install_parser.set_defaults(func=lambda args: install_dependencies(args))
    
    run_parser = subparsers.add_parser("run", help="Run a script defined in ezy.json (e.g., 'ezy run dev' or 'ezy run start')")
    run_parser.add_argument("script", nargs="?", help="Name of the script to run")
    run_parser.set_defaults(func=lambda args: run_script(args))
    
    build_parser = subparsers.add_parser("build", help="Build the project (syntax check)")
    build_parser.set_defaults(func=lambda args: build_project())
    
    serve_parser = subparsers.add_parser("serve", help="Start the development server")
    serve_parser.set_defaults(func=lambda args: serve_project())
    
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.set_defaults(func=lambda args: test_project())
    
    lint_parser = subparsers.add_parser("lint", help="Run code linting")
    lint_parser.set_defaults(func=lambda args: lint_project())
    
    info_parser = subparsers.add_parser("info", help="Show CLI and system information")
    info_parser.set_defaults(func=lambda args: info_project())
    
    update_parser = subparsers.add_parser("update", help="Update the CLI (simulation)")
    update_parser.set_defaults(func=lambda args: update_cli())
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    args.func(args)

if __name__ == "__main__":
    main()
