# ML

학습, 평가, confidence calibration, 시간 순서 보존 백테스트 코드를 이 디렉터리에 둡니다.

`backtest.py`는 사건별 시간 순서를 유지해 Brier score, precision/recall, 조기경보 리드타임을 계산합니다.
예: `py services/ml/backtest.py data/synthetic/backtest_cases.jsonl`

`prepare_datasets.py`는 KOLD·BEEP·K-MHaS 원본을 `data/processed/{train,validation,test}.jsonl`의 공통 포맷으로 변환합니다. 원본·처리 데이터는 Git에서 제외하며, 출처와 사용 제한은 루트의 `DATASET_LICENSES.md`에서 관리합니다.

`train_text_classifier.py`는 공통 `harmful` 레이블로 `klue/roberta-base` 이진 분류기를 파인튜닝합니다. GPU가 있으면 FP16을 사용합니다. 예: `python services/ml/train_text_classifier.py --epochs 1 --max-train-samples 20000 --max-validation-samples 5000`
