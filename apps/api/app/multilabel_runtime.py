from pathlib import Path
import os

MODEL_DIR = Path(os.getenv("MOBIUS_MULTILABEL_MODEL_DIR", str(Path.cwd() / "artifacts" / "multilabel-classifier" / "best")))

class MultiLabelClassifier:
    def __init__(self): self.model = self.tokenizer = self.torch = None; self.error = None
    def predict(self, texts: list[str]) -> dict[str, float]:
        if self.model is None:
            try:
                import torch
                from transformers import AutoModelForSequenceClassification, AutoTokenizer
                self.torch, self.tokenizer = torch, AutoTokenizer.from_pretrained(MODEL_DIR)
                self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR); self.model.eval()
            except Exception as error: self.error = str(error); return {}
        with self.torch.no_grad():
            tokens = self.tokenizer(texts, padding=True, truncation=True, max_length=160, return_tensors="pt")
            probabilities = self.torch.sigmoid(self.model(**tokens).logits).mean(dim=0).tolist()
        return {self.model.config.id2label[str(index)] if str(index) in self.model.config.id2label else self.model.config.id2label[index]: round(value, 4) for index, value in enumerate(probabilities)}

multilabel_classifier = MultiLabelClassifier()
