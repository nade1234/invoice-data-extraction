# DWEXO-OCR API

## Description

DWEXO-OCR is a FastAPI-based web service for extracting text from PDF and image files using the OCR.Space API. It handles large PDFs by splitting pages or converting them to images, and returns plain text for easy integration.

## Features

* OCR on PDFs and common image formats (JPG, PNG, TIFF, BMP)
* Automatic splitting of large PDFs (> 1 MB) for OCR
* Fallback to image-based OCR on PDF processing failure
* Single endpoint for batch processing of multiple files
* Docker support for containerized deployment

## Requirements

* Python 3.12+
* [Poppler](https://github.com/oschwartz10612/poppler-windows/releases/) (for `pdf2image` on Windows)
* Docker (optional, for containerized deployment)

### Python Dependencies

Managed via `requirements.txt`. Key packages include:

```txt
fastapi==0.116.1
uvicorn==0.35.0
python-dotenv==1.1.1
requests==2.32.4
PyPDF2==3.0.1
pdf2image==1.17.0
pillow==11.3.0
python-multipart==0.0.20
```

## Installation

1. **Clone the repository**

   ```bash
   git clone git@gitlab.com:cherry-soft/dwexo-ocr.git
   cd dwexo-ocr
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   # Windows
   . .venv/Scripts/activate
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install --no-cache-dir -r requirements.txt
   ```

4. **Configure environment variables**
   Create a file `.env` in the project root with:

   ```env
   OCR_API_KEY=your_ocr_space_api_key
   ```

## Running Locally

Start the server with Uvicorn:

```bash
uvicorn ocr_api:app --reload --host 0.0.0.0 --port 8000
```

Open your browser at `http://localhost:8000/docs` to access the interactive Swagger UI.

## API Usage

### POST `/ocr_extract/`

* **Description**: Accepts one or more PDF/image files and returns the extracted text.
* **Request**: `multipart/form-data` field `files` with file uploads.
* **Response**: `text/plain` containing concatenated OCR results.

**Example using `curl`:**

```bash
curl -X POST "http://localhost:8000/ocr_extract/" \
  -F "files=@/path/to/document.pdf" \
  -F "files=@/path/to/image.jpg"
```

## Docker

Build the Docker image:

```bash
docker build -t dwexo-ocr:latest .
```

Run a container:

```bash
docker run -d \
  -p 8000:8000 \
  -e OCR_API_KEY=your_ocr_space_api_key \
  --name dwexo-ocr \
  dwexo-ocr:latest
```

Access the API at `http://localhost:8000/docs` inside your browser.

## Contributing

Contributions are welcome! Feel free to open issues or submit merge requests.

## License

This project is licensed under the MIT License.
