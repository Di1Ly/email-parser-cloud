import pytest
from app.parser import parse_eml_file

# Создаем заглушку EML файла для тестирования (в реальном тесте используется временный файл)
@pytest.fixture
def mock_eml_bytes():
    # Это должна быть заглушка, имитирующая содержимое EML
    return b"Subject: Test Subject\nFrom: Sender <sender@example.com>\nTo: Receiver <receiver@example.com>\nDate: Mon, 27 Aug 2026 12:00:00 +0300\nContent-Type: text/plain; charset=utf-8\n\nThis is the plain text body."

def test_successful_parsing(mock_eml_bytes):
    """Тестирует успешный разбор EML и извлечение основных полей."""
    try:
        result = parse_eml_file(mock_eml_bytes)
        
        # 1. Проверка успеха
        assert result['ok'] is True
        
        # 2. Subject (проверяем, что поле присутствует и не null)
        assert result['headers']['subject'] is not None
        
        # 3. From
        assert "sender@example.com" in result['headers']['from']
        
        # 4. To
        assert "receiver@example.com" in result['headers']['to']

        # 5. Plain text (проверяем, что текст извлечен)
        assert result['body']['text'] is not None and len(result['body']['text']) > 10
        
        # 6. Отсутствие вложений (для заглушки)
        assert result['attachments']['count'] == 0

    except Exception as e:
        pytest.fail(f"Тест провалился с ошибке: {e}")