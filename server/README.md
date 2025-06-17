# 매일메일 FastAPI 서버

매일메일 서비스의 FastAPI 서버입니다.

## 📖 API Docs

[![alt text](/assets/api-docs.png)](https://chobab.jagaldol.com/docs)

> [API 문서는 여기](https://chobab.jagaldol.com/docs)서 확인할 수 있습니다.

## ⚡ Getting Started

### 🛠️ MySQL 환경 변수 설정

```shell
cp server/.mysql.env.example server/.mysql.env
```

🔑 MySQL 관련 설정을 `.mysql.env` 파일에 추가하세요.

### 🏗️ MySQL 실행

```shell
docker-compose -f server/docker-compose.yml up -d
```

✅ docker-compose를 사용하여 MySQL을 실행합니다.

### 🌍 FastAPI 서버 환경 변수 설정

FastAPI 서버는 **루트 프로젝트의 `.env` 파일**을 공유합니다.

- **SESSION_KEY**와 **MySQL** 관련 환경 변수를 `.env`에 추가하세요.

### 📦 가상 환경 생성

```shell
python -m venv .venv
```

### 📌 FastAPI 서버 패키지 설치

```shell
pip install -r server/requirements.txt
```

**⚠️ 주의:**

- 서버 실행에 필요한 패키지만 설치합니다.
- 루트 폴더의 `requirements.txt`를 사용하여 전체 설치할 필요가 없습니다.

### 🚀 FastAPI 서버 실행

```shell
uvicorn server.app:app
```

✅ `uvicorn`을 사용하여 FastAPI 서버를 실행합니다.
