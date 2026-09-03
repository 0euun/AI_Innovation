"""개인정보 없는 JSONL 시나리오를 시간 압축해 재생하는 입력 어댑터."""

from collections.abc import Iterator
from pathlib import Path
import json

from schemas import NormalizedEvent


def load_replay(path: Path) -> Iterator[NormalizedEvent]:
    """한 줄씩 검증해 반환한다. 운영 환경에서는 공식 API Connector와 동일 계약을 사용한다."""
    with path.open(encoding="utf-8") as source:
        for line in source:
            if line.strip():
                yield NormalizedEvent.model_validate(json.loads(line))

