서비스만 작성을 하면 컨트롤러를 자동으로 작성해주는, 프레임워크
# Ezy API

API 생성 및 프로젝트 관리를 위한 프레임워크입니다. Ezy API를 사용하면 컨트롤러 없이도 서비스 클래스만으로 자동으로 REST API 엔드포인트가 생성됩니다.

## 특징

- 서비스 기반 API 생성
- 자동 엔드포인트 생성
- 간편한 프로젝트 관리를 위한 CLI 도구
- SQLite 데이터베이스 통합

## 설치

```bash
pip install ezyapi
```

## CLI 사용법

`Ezy CLI`는 **Ezy API** 프로젝트를 쉽고 간편하게 관리하고, 자동으로 API 엔드포인트를 생성할 수 있는 CLI 도구입니다. 이 도구는 서비스를 기반으로 API를 구축하며, 서비스 컴포넌트만으로 RESTful API를 자동으로 생성할 수 있습니다.

## 기능

- **서비스 기반 API 생성**: 서비스 클래스를 작성하면 자동으로 엔드포인트가 생성됩니다.
- **자동 엔드포인트 생성**: 컨트롤러 없이 서비스만으로 REST API 엔드포인트가 자동으로 생성됩니다.
- **SQLite 통합**: 프로젝트 생성 시 기본 SQLite 데이터베이스를 설정하여 빠르게 프로젝트를 시작할 수 있습니다.
- **CLI 도구**: `Ezy API CLI`는 프로젝트 생성, 서비스 생성, 개발 서버 실행 등 다양한 기능을 제공합니다.

## 설치

`Ezy API CLI`를 사용하려면 먼저 `ezyapi` 패키지를 설치해야 합니다.

```bash
pip install ezyapi

```bash
# 새 프로젝트 생성
ezy new 프로젝트명

# 서비스 컴포넌트 생성
ezy generate service 서비스명

# 엔티티 컴포넌트 생성
ezy generate entity 엔티티명

# 개발 서버 실행
ezy serve

# 구문 검사
ezy build

# 테스트 실행
ezy test

# 코드 린팅
ezy lint

# 버전 정보 출력
ezy info
```
