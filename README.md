# =============================================================================
# Email Parser Cloud Service Documentation
# =============================================================================

## Overview
This service provides a robust and reliable backend for parsing raw EML (Email Message Format) 
bytes into structured, machine-readable JSON data. It is designed to handle the complexities 
of modern email formats, including various MIME types, international character sets, 
and embedded attachments, ensuring that core content and file data are cleanly separated.

## Core Functionality
The service uses Python's standard `email` library combined with custom logic to:
1.  **Header Extraction:** Accurately parse all standard headers (From, To, Subject, Date, etc.), 
    including proper decoding of non-ASCII characters in subjects and headers.
2.  **Body Parsing:** Support multiple body formats within a single email:
    *   `text/plain`: Standard plain text content.
    *   `text/html`: HTML formatted content.
    *   `multipart/alternative`: Concatenates both plain and HTML versions, prioritizing readability.
3.  **Attachment Handling:** Identify and extract all attachments (including inline files) 
    based on `Content-Disposition`. Attachments are kept separate from the main body text.

## API Endpoint: POST /parse
This endpoint accepts a single file upload containing raw EML bytes.

**Request:**
*   **Method:** `POST`
*   **Content-Type:** `multipart/form-data`
*   **Body Parameter:** `file` (The uploaded EML file)

**Response (JSON):**
A successful request returns a JSON object containing the parsed structure:

```json
{
  "success": true,
  "metadata": {
    "From": "sender@example.com",
    "To": "recipient@example.com",
    "Subject": "Тестовое письмо с кириллицей",
    "Date": "Fri, 27 Aug 2026 10:00:00 +0300",
    // ... other headers
  },
  "body": "The combined plain text content from the email body.",
  "attachments": [
    {
      "filename": "report.pdf",
      "content_type": "application/pdf",
      "size": 12345,
      "content": "[Decoded binary content of the attachment]"
    },
    // ... more attachments
  ]
}
```

**Error Handling:**
If parsing fails (e.g., malformed EML), a `400 Bad Request` is returned with an error message detailing the failure.

## Supported MIME Scenarios
The parser robustly handles:
*   Simple single-part emails (`text/plain`).
*   Emails with international characters in headers and subjects (e.g., Cyrillic).
*   Multipart alternatives (`multipart/alternative`) containing both `text/plain` and `text/html`.
*   Multipart mixed content (`multipart/mixed`), which can contain a combination of body text, multiple attachments, and inline files.

## Attachment Processing Details
1.  **Identification:** Attachments are identified via MIME headers like `Content-Disposition: attachment; filename="..."` or `inline`.
2.  **Extraction:** The parser extracts the raw content bytes, decodes them (using detected charset), and stores them in the `attachments` array.
3.  **Separation:** Crucially, the decoded content of attachments is *never* included in the main `body` field, ensuring clean separation of concerns.

## Current Limitations
*   The service assumes that if multiple body parts exist (e.g., text/plain and text/html), they should be concatenated into a single string for simplicity. Complex merging logic based on MIME type priority is not implemented.
*   File content in attachments is returned as a decoded string representation; binary integrity checks are recommended for critical file types.