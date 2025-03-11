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
