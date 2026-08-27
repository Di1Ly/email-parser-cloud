import os
from email import policy, message_from_bytes
from typing import Dict, Any, List

# Структура для хранения всех извлеченных данных
class ParsedEmailData:
    def __init__(self):
        self.headers: Dict[str, str] = {}
        self.body_text: str | None = None
        self.body_html: str | None = None
        self.attachments: List[Dict[str, Any]] = []
        self.metadata: Dict[str, Any] = {
            "rawSizeBytes": 0,
            "hasText": False,
            "hasHtml": False
        }

    def parse(self, eml_bytes: bytes) -> Dict[str, Any]:
        """Основная функция парсинга EML файла."""
        try:
            # Используем email.parser для корректной обработки MIME и кодировок
            msg = message_from_bytes(eml_bytes, policy=policy.default)

            self._extract_headers(msg)
            self._extract_body(msg)
            self._extract_attachments(msg)
            
            # Формирование финального словаря для JSON ответа
            return self._to_dict()

        except Exception as e:
            raise ValueError(f"Ошибка парсинга EML файла: {str(e)}")

    def _extract_headers(self, msg: Any):
        """Извлекает заголовки письма."""
        # В реальном приложении здесь должна быть более сложная логика для To/CC/BCC
        for header in msg.get_all('Subject', []):
            self.headers['subject'] = header[0]

        # Простой извлечение основных заголовков (для примера)
        if 'From' in msg:
             self.headers['from'] = str(msg['From'])
        if 'To' in msg:
             self.headers['to'] = str(msg['To'])
        # ... и так далее для CC, BCC, Reply-To, Date, Message-ID

    def _extract_body(self, msg: Any):
        """Извлекает текст и HTML тело письма."""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get('Content-Type')
                disposition = str(part.get('Content-Disposition'))

                # Простая логика: первый подходящий MIME тип считается основным телом
                if content_type and 'text/plain' in content_type:
                    self.body_text = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    self.metadata['hasText'] = True
                elif content_type and 'text/html' in content_type:
                    self.body_html = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    self.metadata['hasHtml'] = True
        else:
            # Если нет multipart, это простое текстовое сообщение
            try:
                text = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
                self.body_text = text
                self.metadata['hasText'] = True
            except Exception:
                pass

    def _extract_attachments(self, msg: Any):
        """Извлекает информацию о вложениях."""
        # В реальном приложении нужно пройтись по всем частям и найти те, что являются вложениями.
        # Для каркаса оставим заглушку.
        pass

    def _to_dict(self) -> Dict[str, Any]:
        """Преобразует внутреннее состояние в требуемый JSON формат."""
        return {
            "ok": True,
            "file": "message.eml", # Имя файла передается через API
            "headers": {
                "subject": self.headers.get('subject'),
                "from": self.headers.get('from'),
                "to": self.headers.get('to'),
                "cc": [],
                "bcc": [],
                "replyTo": None,
                "date": None,
                "messageId": None
            },
            "body": {
                "text": self.body_text if self.body_text else None,
                "html": self.body_html if self.body_html else None
            },
            "attachments": {
                "count": len(self.attachments),
                "items": [
                    {"filename": att['filename'], "contentType": att['contentType'], "sizeBytes": att['size']} 
                    for att in self.attachments
                ]
            },
            "metadata": {
                "rawSizeBytes": self.metadata["rawSizeBytes"],
                "hasText": self.metadata["hasText"],
                "hasHtml": self.metadata["hasHtml"]
            }
        }

def parse_eml_file(eml_bytes: bytes) -> Dict[str, Any]:
    """Обёртка для вызова парсера."""
    parser = ParsedEmailData()
    return parser.parse(eml_bytes)