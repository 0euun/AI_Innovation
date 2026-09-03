# Workers

`schemas.py`는 모든 Platform Connector가 출력해야 하는 개인정보 최소화 공통 이벤트 계약입니다. 원본 플랫폼 계정 ID 대신 `author_ref`를 사용합니다.

`replay.py`는 `data/synthetic/demo_events.jsonl`을 읽는 synthetic replay 입력 어댑터입니다. 이후 공식 API·고객 업로드·웹훅 Connector도 같은 `NormalizedEvent`를 출력합니다.

