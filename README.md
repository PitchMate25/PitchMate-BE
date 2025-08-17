# PitchMate-BE

FastAPI + MongoDB를 Docker Compose로 실행

## 빠른 시작
```bash
# 1) 의존 설치는 Docker가 처리합니다.
cp .env.example .env   # 실제 비밀값으로 수정

# 2) 실행
docker compose up --build -d

# 3) 확인
## API 문서
http://localhost:8000/docs
## 헬스 체크
http://localhost:8000/health
## Mongo 웹 콘솔 (mongo-express)
http://localhost:8081
```
