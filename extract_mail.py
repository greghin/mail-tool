#!/usr/bin/env python3
"""
Walk an Unsorted/ folder of scanned PDFs and produce a JSON manifest containing
the extracted text per file. Uses pdftotext when the PDF already has a text
layer, falls back to OCR (pdftoppm + tesseract) for image-only scans.

Output: manifest.json (or path given as second arg), with shape
{
  "generated_at": "...",
  "items": [
    {
      "path": "...",
      "filename": "...",
      "size_bytes": 12345,
      "num_pages": 2,
      "method": "pdftotext" | "ocr",
      "text": "...first ~6000 chars..."
    },
    ...
  ]
}
"""

import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

MAX_CHARS = 6000          # cap extracted text per file
MIN_DIRECT_TEXT = 80      # if direct text under this length, fall back to OCR
OCR_DPI = 250


def run(cmd, **kwargs):
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def pdf_num_pages(pdf_path: Path) -> int:
    res = run(["pdfinfo", str(pdf_path)])
    for line in res.stdout.splitlines():
        if line.startswith("Pages:"):
            try:
                return int(line.split(":", 1)[1].strip())
            except ValueError:
                return 0
    return 0


def extract_with_pdftotext(pdf_path: Path) -> str:
    res = run(["pdftotext", "-layout", str(pdf_path), "-"])
    return res.stdout or ""


def extract_with_ocr(pdf_path: Path) -> str:
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        run(["pdftoppm", "-r", str(OCR_DPI), str(pdf_path), str(td_path / "page"), "-png"])
        pages = sorted(td_path.glob("page-*.png"))
        out_parts = []
        for img in pages:
            res = run(["tesseract", str(img), "-", "-l", "eng"])
            out_parts.append(res.stdout)
        return "\n".join(out_parts)


def extract_text(pdf_path: Path) -> tuple[str, str]:
    """Return (text, method)."""
    direct = extract_with_pdftotext(pdf_path).strip()
    if len(direct) >= MIN_DIRECT_TEXT:
        return direct, "pdftotext"
    ocr = extract_with_ocr(pdf_path).strip()
    if len(ocr) > len(direct):
        return ocr, "ocr"
    return direct, "pdftotext"


def main():
    if len(sys.argv) < 2:
        print("usage: extract_mail.py <unsorted_dir> [<manifest_out_path>]", file=sys.stderr)
        sys.exit(2)

    unsorted_dir = Path(sys.argv[1]).expanduser()
    manifest_path = Path(sys.argv[2]) if len(sys.argv) >= 3 else Path(__file__).resolve().parent / "manifest.json"

    if not unsorted_dir.is_dir():
        print(f"not a directory: {unsorted_dir}", file=sys.stderr)
        sys.exit(2)

    pdfs = sorted(p for p in unsorted_dir.iterdir() if p.suffix.lower() == ".pdf" and not p.name.startswith("."))
    if not pdfs:
        print(f"no PDFs found in {unsorted_dir}")
        manifest_path.write_text(json.dumps({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "unsorted_dir": str(unsorted_dir),
            "items": [],
        }, indent=2))
        return

    items = []
    for i, pdf in enumerate(pdfs, 1):
        print(f"[{i}/{len(pdfs)}] {pdf.name}", flush=True)
        try:
            text, method = extract_text(pdf)
        except Exception as e:
            text, method = f"<extraction error: {e}>", "error"
        items.append({
            "path": str(pdf),
            "filename": pdf.name,
            "size_bytes": pdf.stat().st_size,
            "num_pages": pdf_num_pages(pdf),
            "method": method,
            "text": text[:MAX_CHARS],
        })

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "unsorted_dir": str(unsorted_dir),
        "items": items,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"wrote {manifest_path} ({len(items)} items)")


if __name__ == "__main__":
    main()
