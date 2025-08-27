# 📄 OCR & Invoice Extractor API

A **FastAPI** service to extract text from PDFs/images using **OCR.Space** and, optionally, transform the result into a structured **invoice JSON** using **Groq LLM**.

---

## — Two Modes (Two Endpoints)

* **OCR only (no LLM)** → `POST /ocr_extract/`

  * Returns **raw text**.
  * **No Groq key required**.
* **OCR + LLM (structured invoice)** → `POST /ocr_extract_llm/`

  * Returns **structured JSON** (invoice fields).
  * **Requires** `GROQ_API_KEY`.

> Choose `/ocr_extract/` if you only need text. Choose `/ocr_extract_llm/` if you want a normalized invoice JSON.

---

## ✨ Features

* Accepts **PDF** and **image** files: `.pdf`, `.jpg`, `.jpeg`, `.png`, `.tiff`, `.bmp`.
* Handles large PDFs by **splitting per page** or **PDF→image conversion**.
* Smart OCR fallback: if direct OCR fails, converts pages to images and retries.
* Optional **JSON extraction** for invoices via **Groq LLM**.

---

## ⚙️ Requirements

* **Python** ≥ 3.9
* System dependency for `pdf2image`:

  * **Poppler** must be installed and in `PATH`.

    * Ubuntu/Debian: `sudo apt-get install poppler-utils`
    * macOS (Homebrew): `brew install poppler`
    * Windows: install Poppler and add `bin` to PATH (e.g., `C:\poppler-xx\Library\bin`).

---

## 📦 Installation

```bash
git clone https://github.com/nade1234/invoice-data-extraction.git
cd invoice-data-extraction
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows
# .venv\Scripts\activate
pip install -r requirements.txt
```

Create a **.env** file in the project root:

```env
OCR_API_KEY=your_ocrspace_api_key
# Only required if you call /ocr_extract_llm/
GROQ_API_KEY=your_groq_api_key
```

> The app will raise a clear error on startup if either key is missing. If you only plan to use `/ocr_extract/`, you can set a dummy `GROQ_API_KEY` or adjust the startup checks.

---

## ▶️ Run

```bash
uvicorn ocr_api:app --reload --host 0.0.0.0 --port 8000
```

* API root: `http://127.0.0.1:8000`
* Docs (Swagger): `http://127.0.0.1:8000/docs`

---

## 🔌 Endpoints

### 1) OCR only — **No LLM**

`POST /ocr_extract/`

* **Request**: `multipart/form-data` with one or more `files`.
* **Response**: `text/plain` (concatenated raw text from all pages/files).

**cURL**

```bash
curl -X POST "http://127.0.0.1:8000/ocr_extract/" \
  -F "files=@invoice.pdf"
```

**Multiple files**

```bash
curl -X POST "http://127.0.0.1:8000/ocr_extract/" \
  -F "files=@page1.jpg" \
  -F "files=@page2.png"
```

---

### 2) OCR + LLM — **Structured Invoice JSON**

`POST /ocr_extract_llm/`

* **Request**: `multipart/form-data` with one or more `files`.
* **Response**: `application/json` (invoice payload).
* **Requires**: `GROQ_API_KEY`.

**cURL**

```bash
curl -X POST "http://127.0.0.1:8000/ocr_extract_llm/" \
  -F "files=@invoice.pdf"
```

**Example JSON**

```json
{
  "invoiceNumber": "INV-2024-001",
  "invoiceDate": "2024-06-01",
  "dueDate": "2024-07-01",
  "supplier": {
    "name": "ABC Corp",
    "address": "123 Rue Exemple, Paris",
    "email": "info@abccorp.com",
    "phone": "+33 1 23 45 67 89",
    "registrationNumber": "FR123456789"
  },
  "client": {
    "name": "XYZ SARL",
    "address": "45 Boulevard Client, Lyon"
  },
  "items": [
    {
      "reference": "PRD001",
      "description": "Product A",
      "quantity": 2,
      "VAT": 10.0,
      "unitPrice": 50.0,
      "totalPrice": 100.0
    }
  ],
  "subtotal": 100.0,
  "total VAT": 10.0,
  "total amount": 110.0,
  "currency": "EUR",
  "paymentTerms": "30 days",
  "note": "Merci pour votre confiance."
}
```

> 💡 **Decimal rule in prompt**: the LLM is instructed that commas are **decimal separators** (e.g., `1,50 → 1.50`). Periods can be thousands separators depending on context. Validate and normalize as needed.

---

## 🧠 How it works

* **`ocr_space(path)`**: Calls OCR.Space (`language=fre`) and returns parsed text.
* **`split_and_ocr(path)`**: Splits PDFs into single-page PDFs if size exceeds `MAX_SIZE` (1 MB per page). OCRs each page.
* **`ocr_by_images(path)`**: Converts PDF pages to images (`dpi=150`), compresses progressively to fit under 1 MB, then OCRs.
* **`ocr_auto(path)`**: Chooses the best strategy based on file type/size, falls back to image OCR on error.
* **`format_text_with_llm(raw_text)`**: Sends a strict prompt to Groq (`llama3-70b-8192`) and attempts to parse the JSON.

---

## 📏 Limits & Behavior

* **MAX\_SIZE**: `1_000_000` bytes (1 MB) **per page/image** before calling OCR.
* If a page/image cannot be compressed under 1 MB, the code downsizes and retries.
* Supported inputs: `.pdf`, `.jpg`, `.jpeg`, `.png`, `.tiff`, `.bmp`.
* The OCR request uses French (`language=fre`). Adjust if your documents are not in French.

---

## 🧪 Request/Response Summary

| Endpoint                 | Purpose            | Output             | API keys needed               |
| ------------------------ | ------------------ | ------------------ | ----------------------------- |
| `POST /ocr_extract/`     | OCR only           | `text/plain`       | `OCR_API_KEY`                 |
| `POST /ocr_extract_llm/` | OCR + invoice JSON | `application/json` | `OCR_API_KEY`, `GROQ_API_KEY` |

---

## 🧯 Error Handling

* `400` **Bad Request**: Unsupported file extension.
* `500` **Server Error**: OCR failure (with filename and error detail).
* LLM JSON parsing fallback: if parsing fails, returns `{ "raw_llm_response": "..." }`.

> **Tip (code hygiene):** If `format_text_with_llm` already returns a Python `dict`, you can directly return it instead of calling `json.loads` again in `/ocr_extract_llm/`.

---

## 🔐 Security Notes

* Keep `.env` out of version control (`.gitignore`).
* Never log raw API keys.
* Consider adding file-type and size validations at upload boundary (Fast
