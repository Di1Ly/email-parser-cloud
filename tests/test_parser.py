import unittest
from typing import Dict, Any
from app.parser import parse_eml_bytes

class MockEMLData:
    """Helper class to simulate EML bytes for testing."""
    @staticmethod
    def create_plain_text(subject: str, body: str) -> bytes:
        # Minimal structure for a simple text email
        headers = f"Subject: {subject}\r\nFrom: test@example.com\r\nTo: recipient@example.com\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Transfer-Encoding: 7bit\r\n\r\n{body}"
        return headers.encode('utf-8')

    @staticmethod
    def create_multipart_alternative(subject: str, plain_text: str, html_content: str) -> bytes:
        # Minimal structure for multipart/alternative
        headers = f"Subject: {subject}\r\nFrom: test@example.com\r\nTo: recipient@example.com\r\nContent-Type: multipart/alternative; boundary=\"boundary\"\r\n\r\n--boundary\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Transfer-Encoding: 7bit\r\n\r\n{plain_text}\r\n--boundary\r\nContent-Type: text/html; charset=utf-8\r\nContent-Transfer-Encoding: 7bit\r\n\r\n{html_content}\r\n--boundary--\r\n"
        return headers.encode('utf-8')

    @staticmethod
    def create_multipart_mixed_with_attachment(subject: str, body_text: str, attachment_name: str, attachment_content: bytes) -> bytes:
        # Minimal structure for multipart/mixed with an attachment
        headers = f"Subject: {subject}\r\nFrom: test@example.com\r\nTo: recipient@example.com\r\nContent-Type: multipart/mixed; boundary=\"boundary\"\r\n\r\n--boundary\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Transfer-Encoding: 7bit\r\n\r\n{body_text}\r\n--boundary\r\nContent-Disposition: attachment; filename=\"{attachment_name}\"\r\nContent-Type: application/pdf\r\nContent-Transfer-Encoding: base64\r\n\r\n{attachment_content.decode('latin-1')}\r\n--boundary--\r\n"
        return headers.encode('utf-8')

    @staticmethod
    def create_multipart_mixed_with_inline(subject: str, body_text: str, inline_name: str, inline_content: bytes) -> bytes:
        # Minimal structure for multipart/mixed with an inline file
        headers = f"Subject: {subject}\r\nFrom: test@example.com\r\nTo: recipient@example.com\r\nContent-Type: multipart/mixed; boundary=\"boundary\"\r\n\r\n--boundary\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Transfer-Encoding: 7bit\r\n\r\n{body_text}\r\n--boundary\r\nContent-Disposition: attachment; filename=\"{inline_name}\"; name=\"attachment\"\r\nContent-Type: image/png\r\nContent-Transfer-Encoding: base64\r\n\r\n{inline_content.decode('latin-1')}\r\n--boundary--\r\n"
        return headers.encode('utf-8')

class TestEmailParser(unittest.TestCase):

    def setUp(self):
        # Setup common data if needed
        pass

    def test_01_simple_plain_text_email(self):
        """Test case 1: Simple text/plain email."""
        body = "This is a simple plain text message."
        eml_bytes = MockEMLData.create_plain_text("Simple Test", body)
        result = parse_eml_bytes(eml_bytes)

        self.assertIsNotNone(result["body"])
        self.assertEqual(result["body"], body)
        self.assertEqual(len(result["attachments"]), 0)
        self.assertTrue("Subject" in result["headers"])

    def test_02_russian_subject(self):
        """Test case 2: Email with Russian Subject (requires proper decoding)."""
        # Using Cyrillic characters for the subject
        russian_subject = "Тестовое письмо с кириллицей"
        body = "Привет, мир!"
        eml_bytes = MockEMLData.create_plain_text(russian_subject, body)
        result = parse_eml_bytes(eml_bytes)

        self.assertEqual(result["headers"]["Subject"], russian_subject)
        self.assertEqual(result["body"], body)

    def test_03_multipart_alternative(self):
        """Test case 3: multipart/alternative (text/plain + text/html)."""
        plain = "Plain content."
        html = "<html><body><h1>HTML Content</h1><p>Paragraph.</p></body></html>"
        eml_bytes = MockEMLData.create_multipart_alternative("Alt Test", plain, html)
        result = parse_eml_bytes(eml_bytes)

        self.assertIsNotNone(result["body"])
        # Expecting both parts joined by double newline
        expected_body = f"{plain}\n\n{html}"
        self.assertEqual(result["body"], expected_body)
        self.assertEqual(len(result["attachments"]), 0)

    def test_04_multipart_mixed_with_one_attachment(self):
        """Test case 4: multipart/mixed with one attachment."""
        subject = "Mixed Test"
        body = "This is the main body text."
        pdf_content = b"%PDF-1.4\n..." # Mock PDF content
        eml_bytes = MockEMLData.create_multipart_mixed_with_attachment(
            subject, body, "report.pdf", pdf_content
        )
        result = parse_eml_bytes(eml_bytes)

        self.assertIsNotNone(result["body"])
        self.assertEqual(result["body"], body)
        self.assertEqual(len(result["attachments"]), 1)
        attachment = result["attachments"][0]
        self.assertEqual(attachment["filename"], "report.pdf")
        self.assertEqual(attachment["content_type"], "application/pdf")
        # Check size calculation (should match raw bytes length)
        self.assertEqual(attachment["size"], len(pdf_content))

    def test_05_multiple_attachments(self):
        """Test case 5: Email with multiple attachments."""
        subject = "Multi Attachments"
        body = "Body text."
        # Simulate two distinct attachments in the MIME structure (requires manual EML construction or mocking)
        # For simplicity, we test the detection mechanism assuming the parser handles sequential parts.
        # Since MockEMLData is limited, we rely on testing the core logic's ability to detect multiple parts.
        # A full test would require a complex mock EML structure. We verify attachment count > 1 capability.
        
        # Creating a simplified multi-attachment mock (assuming parser handles it)
        mock_eml = f"Subject: {subject}\r\nFrom: t@t.com\r\nTo: r@r.com\r\nContent-Type: multipart/mixed; boundary=\"boundary\"\r\n\r\n--boundary\r\nContent-Disposition: attachment; filename=\"file1.txt\"\r\nContent-Type: text/plain\r\n\r\n{b'content 1'}\r\n--boundary\r\nContent-Disposition: attachment; filename=\"image.png\"\r\nContent-Type: image/png\r\n\r\n{b'content 2'}\r\n--boundary--\r\n"
        eml_bytes = mock_eml.encode('utf-8')

        result = parse_eml_bytes(eml_bytes)
        self.assertEqual(len(result["attachments"]), 2)
        # Check if both files are detected and separated from the body
        self.assertTrue("content 1" in result["attachments"][0]["content"])
        self.assertTrue("content 2" in result["attachments"][1]["content"])

    def test_06_russian_filename(self):
        """Test case 6: Attachment with Russian filename."""
        subject = "Russian File Name Test"
        body = "Body."
        russian_filename = "Отчет.pdf"
        pdf_content = b"%PDF-1.4\n..."
        eml_bytes = MockEMLData.create_multipart_mixed_with_attachment(
            subject, body, russian_filename, pdf_content
        )
        result = parse_eml_bytes(eml_bytes)

        self.assertEqual(len(result["attachments"]), 1)
        attachment = result["attachments"][0]
        self.assertEqual(attachment["filename"], russian_filename)

    def test_07_inline_attachment(self):
        """Test case 7: Inline attachment with filename."""
        subject = "Inline Test"
        body = "Body."
        png_content = b"\x89PNG\r\n..." # Mock PNG content
        eml_bytes = MockEMLData.create_multipart_mixed_with_inline(
            subject, body, "logo.png", png_content
        )
        result = parse_eml_bytes(eml_bytes)

        self.assertEqual(len(result["attachments"]), 1)
        attachment = result["attachments"][0]
        self.assertEqual(attachment["filename"], "logo.png")
        # Verify it was treated as an attachment, not body content
        self.assertTrue("PNG" in attachment["content"])

    def test_08_missing_optional_headers(self):
        """Test case 8: Email missing optional headers (e.g., Cc, Bcc)."""
        # Simple email structure without explicit CC/BCC headers
        body = "Minimal message."
        eml_bytes = MockEMLData.create_plain_text("Minimal", body)
        result = parse_eml_bytes(eml_bytes)

        self.assertIsNotNone(result["metadata"]["Cc"]) # Should be None or missing key, but not crash
        self.assertEqual(len(result["attachments"]), 0)

    def test_09_raw_size_calculation(self):
        """Test case 9: Correct calculation of rawSizeBytes (attachment size)."""
        subject = "Size Test"
        body = "Body."
        pdf_content = b'\x25\x50\x44\x46' * 10 # Mock content, length is 50 bytes
        eml_bytes = MockEMLData.create_multipart_mixed_with_attachment(
            subject, body, "size_test.pdf", pdf_content
        )
        result = parse_eml_bytes(eml_bytes)

        self.assertEqual(len(result["attachments"]), 1)
        # The size should match the length of the raw bytes provided for the attachment payload
        self.assertEqual(result["attachments"][0]["size"], len(pdf_content))


    def test_10_attachment_not_in_body(self):
        """Test case 10: Verify that attachment content does not pollute the main body."""
        subject = "Separation Test"
        body = "This is the clean body."
        attachment_content = b"SECRET DATA" * 5 # Mock data
        eml_bytes = MockEMLData.create_multipart_mixed_with_attachment(
            subject, body, "secret.txt", attachment_content
        )
        result = parse_eml_bytes(eml_bytes)

        self.assertIsNotNone(result["body"])
        self.assertEqual(result["body"], body) # Body should only contain the plain text part
        self.assertTrue("SECRET DATA" in result["attachments"][0]["content"])


if __name__ == '__main__':
    unittest.main()