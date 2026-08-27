from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import json
from typing import Dict, Any

# Импорт парсера
from app.parser import parse_eml_file

app = FastAPI(title="Email Parser Service")

class ParseResponse(BaseModel):
    ok: bool
    error: str | None = None
    data: dict | None = None

@app.post("/parse", response_model=ParseResponse)
async def parse_eml(file: UploadFile = File(...)):
    """
    Принимает EML файл и возвращает структурированный JSON с результатом разбора.
    """
    try:
        # Чтение содержимого файла в байтах
        eml_bytes = await file.read()
        
        # Вызов парсера
        parsed_data = parse_eml_file(eml_bytes)

        return ParseResponse(ok=True, data=parsed_data)

    except ValueError as e:
        # Обработка ошибок парсинга
        raise HTTPException(status_code=400, detail={"ok": False, "error": str(e)})
    except Exception as e:
        # Общая ошибка сервера
        raise HTTPException(status_code=500, detail={"ok": False, "error": f"Внутренняя ошибка сервера: {str(e)}"})