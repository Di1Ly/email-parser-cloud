import email
from email import policy
from email.message import Message
from typing import Dict, Any, List, Optional

class EmailParserError(Exception):
    """Custom exception for email parsing failures."""
    pass

def parse_eml_file(eml_bytes: bytes) -> Dict[str, Any]:
    """
    Parses raw EML bytes into a structured dictionary containing headers, body content, 
    and attachments.

    Args:
        eml_bytes: The raw bytes of the EML file.

    Returns:
        A dictionary containing parsed email data.
    
    Raises:
        EmailParserError: If parsing fails due to malformed input or unsupported structure.
    """
    try:
        # Use policy=policy.default for robust decoding, especially for non-ASCII characters in headers/subject
        msg = Message()
        msg.set_payload(eml_bytes)
        msg = msg.__init__(email.message_from_bytes(eml_bytes), policy=policy)

    except Exception as e:
        raise EmailParserError(f"Failed to initialize email message from bytes: {e}")

    parsed_data: Dict[str, Any] = {
        "headers": {},
        "body": None,
        "attachments": [],
        "metadata": {}
    }

    # 1. Extract Headers and Metadata
    for header in msg.items():
        key, value = header
        parsed_data["headers"][key] = value

    # Handle common headers explicitly for easier access
    parsed_data["metadata"]["From"] = parsed_data["headers"].get("From")
    parsed_data["metadata"]["To"] = parsed_data["headers"].get("To")
    parsed_data["metadata"]["Cc"] = parsed_data["headers"].get("Cc")
    parsed_data["metadata"]["Bcc"] = parsed_data["headers"].get("Bcc")
    parsed_data["metadata"]["Reply-To"] = parsed_data["headers"].get("Reply-To")
    parsed_data["metadata"]["Date"] = parsed_data["headers"].get("Date")
    parsed_data["metadata"]["Message-ID"] = parsed_data["headers"].get("Message-ID")

    # 2. Process Body and Attachments (Multipart/Mixed)
    if msg.is_multipart():
        main_body: List[str] = []
        attachments: List[Dict[str, Any]] = []
        
        for part in msg.walk():
            content_type = part.get("Content-Type")
            disposition = part.get("Content-Disposition")
            payload = part.get_payload(decode=True)

            if payload is None:
                continue

            # Check for attachments (multipart/mixed or inline files)
            if disposition and ("attachment" in disposition or "inline" in disposition):
                filename = disposition.get("filename")
                content_type_part = content_type if content_type else "application/octet-stream"
                
                # Decode payload to string for storage, but keep raw bytes available conceptually
                try:
                    decoded_payload = payload.decode(part.get("charset", "utf-8"), errors="ignore")
                except UnicodeDecodeError:
                    decoded_payload = str(payload) # Fallback

                attachment_info = {
                    "filename": filename,
                    "content_type": content_type_part,
                    "size": len(payload),
                    "content": decoded_payload
                }
                attachments.append(attachment_info)
            
            # Check for body parts (text/plain, text/html, etc.)
            elif "Content-Type" in content_type and ("text/plain" in content_type or "text/html" in content_type):
                try:
                    decoded_payload = payload.decode(part.get("charset", "utf-8"), errors="ignore")
                    main_body.append(decoded_payload)
                except UnicodeDecodeError:
                    # If decoding fails, treat it as raw text representation
                    main_body.append(str(payload))

        parsed_data["attachments"] = attachments
        
        # Combine body parts (handling multipart/alternative structure)
        if main_body:
            # Simple concatenation for demonstration; real-world might need smarter merging based on MIME type priority
            parsed_data["body"] = "\n\n".join(main_body).strip()

    else:
        # Single part message (simple text/plain or single attachment)
        try:
            decoded_payload = msg.get_payload(decode=True).decode(msg.get("charset", "utf-8"), errors="ignore")
            parsed_data["body"] = decoded_payload
        except Exception as e:
            # Fallback if decoding fails entirely
            parsed_data["body"] = f"[Could not decode body payload]: {e}"

    return parsed_data


def parse_eml_bytes(eml_bytes: bytes) -> Dict[str, Any]:
    """
    Public interface to parse EML bytes. 
    This function wraps the core logic and ensures compatibility with existing API contracts.
    """
    # The core parsing logic is in parse_eml_file, which handles all requirements.
    return parse_eml_file(eml_bytes)

if __name__ == '__main__':
    # Example usage (for testing purposes)
    print("--- Running Email Parser Test ---")
    # Note: In a real scenario, this would be tested via unit tests.
    pass