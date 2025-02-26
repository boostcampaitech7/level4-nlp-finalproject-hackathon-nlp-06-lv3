# 매일메일 Chrome Extension

매일메일 서비스의 Chrome Extension 구현입니다.

## 🎬 Demo Page

![demo](/assets/demo2.png)

- **🗂️ 메인 화면**
  - 날짜별 메일 레포트 카드들을 볼 수 있습니다.
- **📑 레포트 화면**
  - 그날의 레포트 및 **✅TODOList**들을 확인가능합니다.
  - 모든 ✅TODOList가 체크되면 메인화면에서도 완료 표시가 됩니다.

## Installation

1. `/assets/chrome_extension.zip`을 다운받아 압축해제합니다.
2. [chrome://extensions](chrome://extensions)에서 우상단의 `개발자 모드`를 활성화합니다.
3. 좌상단의 `압축해제된 확장 프로그램을 로드합니다.`를 선택하여 확장 프로그램을 로드합니다.

## ⚡Getting Started

### 📂 프로젝트 폴더로 이동

React 프로젝트 폴더로 이동합니다:

```shell
cd chrome-extension
```

### 🛠️ `.env` 파일 생성

```shell
# pwd: root project
cd chrome-extension
# pwd: chrome-extension(now project)
cp .env.local.example .env.local
```

🔑OAuth를 위해 발급받은 **Google Client ID**를 입력합니다.

### 📦 패키지 설치

```shell
npm install
```

### 🚀 프로젝트 빌드

```shell
npm run build
```

### 🔥 (Optional) Hot Reload Dev Server 실행

```shell
npm run dev
```

> 📌 Hot Reload Dev Server를 실행하면 코드 변경 사항이 자동으로 반영됩니다.
