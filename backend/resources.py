import json
from pathlib import Path

from pypdf import PdfReader

data = Path(__file__).parent / "data"

facts = json.loads((data / "facts.json").read_text(encoding="utf-8"))
summary = (data / "summary.txt").read_text(encoding="utf-8")
style = (data / "style.txt").read_text(encoding="utf-8")
linkedin = "\n".join(p.extract_text() for p in PdfReader(data / "linkedin.pdf").pages)
