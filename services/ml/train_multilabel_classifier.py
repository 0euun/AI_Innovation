"""K-MHaS 8개 공격 유형 멀티라벨 분류기 학습."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import f1_score
from torch.utils.data import Dataset
from transformers import AutoModelForSequenceClassification, AutoTokenizer, DataCollatorWithPadding, Trainer, TrainingArguments

ROOT = Path(__file__).resolve().parents[2]
LABELS = ["origin_discrimination", "physical_discrimination", "political_discrimination", "profanity", "age_discrimination", "gender_discrimination", "racial_discrimination", "religious_discrimination"]


class KmhasDataset(Dataset):
    def __init__(self, filename: Path, tokenizer: AutoTokenizer, limit: int | None) -> None:
        rows = [json.loads(line) for line in filename.read_text(encoding="utf-8").splitlines() if line.strip()]
        rows = [row for row in rows if row["source"] == "kmhas"][:limit]
        self.tokens = tokenizer([row["text"] for row in rows], truncation=True, max_length=160)
        self.labels = [[float(label in row["labels"]) for label in LABELS] for row in rows]
    def __len__(self) -> int: return len(self.labels)
    def __getitem__(self, index: int):
        item = {key: torch.tensor(value[index]) for key, value in self.tokens.items()}
        item["labels"] = torch.tensor(self.labels[index])
        return item


class MultiLabelTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        loss = torch.nn.BCEWithLogitsLoss()(outputs.logits, labels)
        return (loss, outputs) if return_outputs else loss


def metrics(prediction):
    labels = prediction.label_ids
    predictions = (1 / (1 + np.exp(-prediction.predictions)) >= 0.5).astype(int)
    return {"micro_f1": f1_score(labels, predictions, average="micro", zero_division=0), "macro_f1": f1_score(labels, predictions, average="macro", zero_division=0)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="klue/roberta-base"); parser.add_argument("--epochs", type=float, default=2); parser.add_argument("--limit", type=int, default=40000)
    parser.add_argument("--output", default=str(ROOT / "artifacts" / "multilabel-classifier-candidate"))
    args = parser.parse_args(); processed = ROOT / "data" / "processed"; output = Path(args.output)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    train, valid = KmhasDataset(processed / "train.jsonl", tokenizer, args.limit), KmhasDataset(processed / "validation.jsonl", tokenizer, min(args.limit // 4, 5000))
    model = AutoModelForSequenceClassification.from_pretrained(args.model, num_labels=len(LABELS), problem_type="multi_label_classification", id2label=dict(enumerate(LABELS)))
    training = TrainingArguments(output_dir=str(output), num_train_epochs=args.epochs, per_device_train_batch_size=16, per_device_eval_batch_size=16, eval_strategy="epoch", save_strategy="epoch", load_best_model_at_end=True, metric_for_best_model="macro_f1", greater_is_better=True, fp16=torch.cuda.is_available(), report_to="none", seed=42)
    trainer = MultiLabelTrainer(model=model, args=training, train_dataset=train, eval_dataset=valid, data_collator=DataCollatorWithPadding(tokenizer), compute_metrics=metrics)
    trainer.train(); result = trainer.evaluate(); trainer.save_model(str(output / "best")); tokenizer.save_pretrained(str(output / "best")); (output / "metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8"); print(result)

if __name__ == "__main__": main()
