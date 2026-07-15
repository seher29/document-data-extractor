"""
Document Data Extractor
========================
Reads a PDF (invoice, receipt, purchase order), asks an LLM (via Groq's
free API, running Llama 3.3 70B) to pull out structured fields, then runs
those fields through independent Python validation (validation.py) before
writing the result to output/.

Usage:
    python main.py                          # processes every PDF in sample_documents/
    python main.py path/to/one_file.pdf      # process a single file

Requires GROQ_API_KEY to be set in the environment (see .env.example).
"""

import os
import sys
import json
import glob
import pdfplumber
from groq import Groq
from dotenv import load_dotenv

from validation import validate_extraction

load_dotenv()

MODEL = "llama-3.3-70b-versatile"

EXTRACTION_SCHEMA_PROMPT = """You are a document data extraction engine. You will be given
the raw text of a scanned business document (invoice, receipt, or purchase order).

Extract the following fields and respond with ONLY a single JSON object - no markdown
fences, no commentary, nothing before or after the JSON.

Schema:
{
  "document_type": "invoice" | "receipt" | "purchase_order",
  "vendor_name": string,
  "document_id": string or null,          // invoice #, receipt #, PO #, etc.
  "document_date": string in YYYY-MM-DD format,
  "due_date": string in YYYY-MM-DD format, or null if not present,
  "line_items": [
    {
      "description": string,
      "quantity": number,
      "unit_price": number,
      "line_total": number
    }
  ],
  "subtotal": number or null,
  "tax_amount": number or null,           // null if no tax line exists in the document
  "total": number
}

Rules:
- Use the exact numbers printed in the document. Do not round unless the document rounds.
- If a field genuinely does not appear in the document, use null - do not guess or invent a value.
- All monetary values are plain numbers (no currency symbols, no commas).
- All dates must be normalized to YYYY-MM-DD even if the source document uses a different format.
"""


def extract_text_from_pdf(path: str) -> str:
    text_parts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    return "\n".join(text_parts)


def call_llm_for_extraction(client, document_text: str) -> dict:
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": EXTRACTION_SCHEMA_PROMPT},
            {"role": "user", "content": f"Document text:\n\n{document_text}"},
        ],
    )
    raw = response.choices[0].message.content.strip()

    # Defensive cleanup: strip markdown fences if the model adds them anyway.
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON: {e}\nRaw output:\n{raw}")


def process_file(client, path: str) -> dict:
    filename = os.path.basename(path)
    print(f"\nProcessing {filename} ...")

    document_text = extract_text_from_pdf(path)
    extracted = call_llm_for_extraction(client, document_text)
    validation_result = validate_extraction(extracted)

    if validation_result["valid"]:
        print(f"  Validation: PASSED")
    else:
        print(f"  Validation: {len(validation_result['issues'])} issue(s) found:")
        for issue in validation_result["issues"]:
            print(f"    - {issue}")

    return {
        "source_file": filename,
        "extracted_data": extracted,
        "validation": validation_result,
    }


def main():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("ERROR: GROQ_API_KEY is not set. See .env.example for setup instructions.")
        sys.exit(1)

    client = Groq(api_key=api_key)

    if len(sys.argv) > 1:
        files = [sys.argv[1]]
    else:
        files = sorted(glob.glob("sample_documents/*.pdf"))

    if not files:
        print("No PDF files found in sample_documents/.")
        sys.exit(1)

    os.makedirs("output", exist_ok=True)
    results = []
    for path in files:
        result = process_file(client, path)
        results.append(result)

        out_name = os.path.splitext(os.path.basename(path))[0] + ".json"
        out_path = os.path.join("output", out_name)
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2)
        print(f"  Wrote {out_path}")

    combined_path = "output/all_results.json"
    with open(combined_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nDone. {len(results)} document(s) processed. Combined output: {combined_path}")


if __name__ == "__main__":
    main()
