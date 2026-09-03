# Mobius

집단 온라인 공격의 확산 신호를 탐지하고, 설명 가능한 위험도·증거 패키지·대응 가이드를 제공하는 웹 서비스입니다.

## 구조

- `apps/web`: Next.js 대시보드
- `apps/api`: FastAPI API 및 도메인 계약
- `services/workers`: 수집·분석·PDF 생성 비동기 워커
- `services/ml`: 학습·평가·백테스트 코드
- `data/synthetic`: 개인정보가 없는 재구성 시연 데이터
- `infra`: 이후 배포·관측 설정

## 구현된 데모 흐름

1. synthetic replay 이벤트를 공통 데이터 계약으로 읽습니다.
2. 언급 증가율·플랫폼 간 확산·유해성·협조 행동 의심 신호를 0~1로 정규화합니다.
3. 가중합 위험도와 단계, 근거, 대응 가이드를 API로 제공합니다.
4. 각 이벤트 SHA-256과 패키지 해시를 포함하는 PDF·JSON 증거 ZIP을 생성합니다.
5. 웹 대시보드에서 피해자 보호/B2B 관점을 전환해 시연합니다.
6. `artifacts/text-classifier/best`에 학습 모델이 있으면 KLUE-RoBERTa 유해성 확률을 위험도 입력으로 사용하고, 없으면 규칙 기반 fallback으로 동작합니다.

## API

- `GET /health`
- `GET /v1/dashboard`
- `GET /v1/targets/demo-target/risk`
- `GET /v1/targets/demo-target/events`
- `GET /v1/targets/demo-target/graph`
- `GET /v1/targets/demo-target/evidence-manifest`
- `GET /v1/targets/demo-target/evidence-package`

FastAPI가 실행되면 Swagger UI는 `http://localhost:8000/docs`에서 확인할 수 있습니다.

## 로컬 실행

1. Docker Desktop을 실행한 뒤 `docker compose up --build`로 API·PostgreSQL·Redis를 시작합니다.
2. Node.js 환경에서 `npm.cmd install` 후 `npm.cmd run dev:web`로 웹 대시보드를 시작합니다.

API 상태 확인: `http://localhost:8000/health`
