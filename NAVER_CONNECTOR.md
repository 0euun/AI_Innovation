# NAVER Search 공식 API Connector

NAVER Cloud Platform의 **NAVER API HUB**에서 검색 API 애플리케이션을 등록한 뒤 Client ID와 Client Secret을 `.env`에 입력한다.

```env
NAVER_CLIENT_ID=발급받은_Client_ID
NAVER_CLIENT_SECRET=발급받은_Client_Secret
```

동기화 API:

`POST /v1/targets/{target_id}/connectors/naver-search/sync`

```json
{
  "query": "브랜드X",
  "sources": ["news", "blog", "cafearticle"],
  "display": 20
}
```

지원 소스는 `news`, `blog`, `cafearticle`, `kin`, `webkr`이다. API HUB의 `X-NCP-APIGW-API-KEY-ID`, `X-NCP-APIGW-API-KEY` 인증 방식을 사용한다. 검색 결과의 제목·설명·발행 시각·링크를 확산 신호 이벤트로 저장하며, 원문 페이지를 무단 수집하지 않는다.
