# YouTube 공식 API Connector

## 준비

Google Cloud 프로젝트에서 YouTube Data API v3를 활성화하고 API Key를 발급한다. `.env`에 다음 값을 넣은 뒤 API 컨테이너를 재기동한다.

```env
YOUTUBE_API_KEY=발급받은_API_KEY
```

## 동기화 API

`POST /v1/targets/{target_id}/connectors/youtube/sync`

```json
{
  "query": "브랜드X",
  "max_videos": 3,
  "max_comments_per_video": 30
}
```

YouTube 공개 영상 검색 결과의 최신 영상과 게시된 댓글만 가져온다. 댓글 비활성화 영상은 건너뛰며, 결과는 `events:ingest`와 동일하게 tenant별 마스킹 이벤트로 저장된다. API quota와 YouTube 정책을 준수하도록 소량 동기화부터 사용한다.
