"""KOLD·BEEP·K-MHaS 원본을 Mobius 공통 JSONL 학습 포맷으로 변환한다.

원본 텍스트를 출력하지 않으며, 레이블 없는 BEEP 테스트 파일은 학습 대상에서 제외한다.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
OUTPUT = ROOT / "data" / "processed"
KMHAS_LABELS = {
    "0": "origin_discrimination", "1": "physical_discrimination", "2": "political_discrimination",
    "3": "profanity", "4": "age_discrimination", "5": "gender_discrimination",
    "6": "racial_discrimination", "7": "religious_discrimination", "8": "none",
}


def split_kold(identifier: str) -> str:
    bucket = int(sha256(identifier.encode("utf-8")).hexdigest(), 16) % 100
    return "train" if bucket < 80 else "validation" if bucket < 90 else "test"


def record(identifier: str, source: str, split: str, text: str, labels: list[str], harmful: bool) -> dict:
    return {"id": identifier, "source": source, "split": split, "text": text, "labels": labels, "harmful": harmful}


def load_kold() -> list[dict]:
    source = json.loads((RAW / "KOLD" / "data" / "kold_v1.json").read_text(encoding="utf-8"))
    return [record(item["guid"], "kold", split_kold(item["guid"]), item["comment"], ["offensive"] if item["OFF"] else ["none"], bool(item["OFF"])) for item in source]


def load_beep(filename: str, split: str) -> list[dict]:
    path = RAW / "korean-hate-speech" / "labeled" / filename
    lines = path.read_text(encoding="utf-8").splitlines()
    header = lines[0].split("\t")
    rows = []
    for index, line in enumerate(lines[1:]):
        values = dict(zip(header, line.split("\t")))
        hate = values["hate"]
        labels = [f"hate_{hate}"]
        if values["contain_gender_bias"].lower() == "true":
            labels.append("gender_bias")
        rows.append(record(f"beep-{split}-{index:05d}", "beep", split, values["comments"], labels, hate != "none"))
    return rows


def load_kmhas(filename: str, split: str) -> list[dict]:
    rows = []
    lines = (RAW / "K-MHaS" / "data" / filename).read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines[1:]):  # 첫 행: document\tlabel
        text, raw_labels = line.rsplit("\t", 1)
        labels = [KMHAS_LABELS[label] for label in raw_labels.split(",")]
        rows.append(record(f"kmhas-{split}-{index:06d}", "kmhas", split, text, labels, labels != ["none"]))
    return rows


def main() -> None:
    records = [
        *load_kold(),
        *load_beep("train.tsv", "train"), *load_beep("dev.tsv", "validation"),
        *load_kmhas("kmhas_train.txt", "train"), *load_kmhas("kmhas_valid.txt", "validation"), *load_kmhas("kmhas_test.txt", "test"),
    ]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for split in ("train", "validation", "test"):
        destination = OUTPUT / f"{split}.jsonl"
        with destination.open("w", encoding="utf-8") as target:
            for item in records:
                if item["split"] == split:
                    target.write(json.dumps(item, ensure_ascii=False) + "\n")
    manifest = {
        "format": "mobius.training.v1",
        "record_count": len(records),
        "by_split": dict(Counter(item["split"] for item in records)),
        "by_source": dict(Counter(item["source"] for item in records)),
        "excluded": ["BEEP test.no_label.tsv: labels unavailable, training and supervised evaluation에서 제외"],
        "label_map": {"kmhas": KMHAS_LABELS},
    }
    (OUTPUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
