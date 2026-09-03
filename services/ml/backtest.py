"""시간 누수를 막는 조기경보 백테스트 유틸리티.

입력 JSONL은 `timestamp`, `actual_risk`, `prediction`, `alert` 필드를 가진다고 가정한다.
실제 사건 데이터와 재구성 데이터 모두 같은 방식으로 평가할 수 있다.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path


@dataclass(frozen=True)
class BacktestResult:
    brier_score: float
    precision: float
    recall: float
    lead_time_minutes: float | None


def evaluate(records: list[dict], risk_threshold: float = 0.7) -> BacktestResult:
    """시간순 레코드에 대해 예측 신뢰도와 경보의 조기 탐지 시간을 계산한다."""
    ordered = sorted(records, key=lambda row: row["timestamp"])
    predictions = [float(row["prediction"]) for row in ordered]
    actuals = [int(bool(row["actual_risk"])) for row in ordered]
    alerts = [bool(row.get("alert", prediction >= risk_threshold)) for row, prediction in zip(ordered, predictions)]
    brier = sum((prediction - actual) ** 2 for prediction, actual in zip(predictions, actuals)) / max(len(ordered), 1)
    true_positive = sum(alert and actual for alert, actual in zip(alerts, actuals))
    false_positive = sum(alert and not actual for alert, actual in zip(alerts, actuals))
    false_negative = sum(not alert and actual for alert, actual in zip(alerts, actuals))
    precision = true_positive / max(true_positive + false_positive, 1)
    recall = true_positive / max(true_positive + false_negative, 1)
    first_alert = next((row["timestamp"] for row, alert in zip(ordered, alerts) if alert), None)
    first_actual = next((row["timestamp"] for row, actual in zip(ordered, actuals) if actual), None)
    lead = None
    if first_alert and first_actual:
        lead = (datetime.fromisoformat(first_actual.replace("Z", "+00:00")) - datetime.fromisoformat(first_alert.replace("Z", "+00:00"))).total_seconds() / 60
    return BacktestResult(round(brier, 4), round(precision, 4), round(recall, 4), lead)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    arguments = parser.parse_args()
    with arguments.input.open(encoding="utf-8") as source:
        result = evaluate([json.loads(line) for line in source if line.strip()])
    print(result)
