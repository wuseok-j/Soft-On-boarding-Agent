# Soft On-boarding Agent

GitHub 데이터를 분석하여 신규 구성원을 위한 맞춤형 온보딩 다이어그램을 제공하는 B2B SaaS 솔루션입니다.

## 프로젝트 구조

- `frontend/`: React (Vite, React Flow) 기반 프론트엔드
- `backend/`: Spring Boot 기반 백엔드

---

## 실행 방법

백엔드와 프론트엔드를 동시에 실행하는 세 가지 방법입니다.

### 1. VS Code 빌드 작업 (추천)
VS Code 터미널의 개별 탭에서 동시에 구동되어 조작이 편리합니다.
- 단축키 `Ctrl + Shift + B` 입력 후 **`Run All (Dev)`** 선택

### 2. PowerShell 스크립트 (Windows)
두 서버가 각각 개별 PowerShell 창으로 분리되어 실행됩니다.
```powershell
.\run-dev.ps1
```

### 3. npm `concurrently` (통합 터미널)
하나의 터미널 창에 프론트/백엔드 로그가 병합되어 출력됩니다.
```bash
# 의존성 설치 (최초 1회)
npm install

# 동시 실행
npm run dev
```

---

## 개별 실행

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
./gradlew bootRun
```
