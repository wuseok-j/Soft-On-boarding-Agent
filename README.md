# Soft On-boarding Agent

B2B SaaS 솔루션: 신규 구성원의 GitHub 데이터를 분석해 4-Way View 다이어그램으로 맞춤형 온보딩을 제공하는 서비스.

## 프로젝트 구조

- `frontend/`: React (Vite) 기반의 프론트엔드 서비스
- `backend/`: Spring Boot 기반의 백엔드 서비스

## 실행 방법

### Frontend 실행
```bash
cd frontend
npm install
npm run dev
```
기본적으로 `http://localhost:5173` 에서 실행됩니다.

### Backend 실행
```bash
cd backend
./gradlew bootRun
```
기본적으로 `http://localhost:8080` 에서 실행됩니다.
