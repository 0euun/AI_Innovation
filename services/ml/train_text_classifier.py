"""Mobius 이진 유해성 분류기 파인튜닝.

KOLD·BEEP·K-MHaS의 공통 harmful 레이블을 이용한다. 세부 유형 멀티라벨 모델은
이 베이스라인 검증 후 별도 헤드로 확장한다.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import torch
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from torch.utils.data import Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer, DataCollatorWithPadding, Trainer, TrainingArguments


ROOT = Path(__file__).resolve().parents[2]


class JsonlDataset(Dataset):
    def __init__(self, path: Path, tokenizer: Any, max_length: int, limit: int | None = None) -> None:
        rows = []
        with path.open(encoding="utf-8") as source:
            for line in source:
                if line.strip():
                    rows.append(json.loads(line))
                    if limit and len(rows) >= limit:
                        break
        self.encodings = tokenizer([row["text"] for row in rows], truncation=True, max_length=max_length)
        self.labels = [int(row["harmful"]) for row in rows]

    def __len__(self) -> int:
        return len(self.labels)

    def __getitem__(self, index: int) -> dict[str, torch.Tensor]:
        item = {key: torch.tensor(value[index]) for key, value in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[index])
        return item


def metrics(prediction: Any) -> dict[str, float]:
    labels = prediction.label_ids
    predictions = np.argmax(prediction.predictions, axis=-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average="binary", zero_division=0)
    return {"accuracy": accuracy_score(labels, predictions), "precision": precision, "recall": recall, "f1": f1}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="klue/roberta-base")
    parser.add_argument("--epochs", type=float, default=2.0)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--max-length", type=int, default=160)
    parser.add_argument("--max-train-samples", type=int, default=None)
    parser.add_argument("--max-validation-samples", type=int, default=None)
    parser.add_argument("--output", default=str(ROOT / "artifacts" / "text-classifier-candidate"))
    arguments = parser.parse_args()

    processed = ROOT / "data" / "processed"
    output = Path(arguments.output)
    tokenizer = AutoTokenizer.from_pretrained(arguments.model)
    train = JsonlDataset(processed / "train.jsonl", tokenizer, arguments.max_length, arguments.max_train_samples)
    validation = JsonlDataset(processed / "validation.jsonl", tokenizer, arguments.max_length, arguments.max_validation_samples)
    model = AutoModelForSequenceClassification.from_pretrained(arguments.model, num_labels=2)
    training = TrainingArguments(
        output_dir=str(output), num_train_epochs=arguments.epochs,
        per_device_train_batch_size=arguments.batch_size, per_device_eval_batch_size=arguments.batch_size,
        eval_strategy="epoch", save_strategy="epoch", logging_steps=50,
        load_best_model_at_end=True, metric_for_best_model="f1", greater_is_better=True,
        fp16=torch.cuda.is_available(), report_to="none", seed=42,
    )
    trainer = Trainer(
        model=model, args=training, train_dataset=train, eval_dataset=validation,
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer), compute_metrics=metrics,
    )
    trainer.train()
    result = trainer.evaluate()
    trainer.save_model(str(output / "best"))
    tokenizer.save_pretrained(str(output / "best"))
    (output / "metrics.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / "training_manifest.json").write_text(json.dumps({
        "model": arguments.model, "train_samples": len(train), "validation_samples": len(validation),
        "device": "cuda" if torch.cuda.is_available() else "cpu", "epochs": arguments.epochs,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
