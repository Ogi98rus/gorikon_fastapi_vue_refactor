from fastapi import APIRouter
from fastapi.responses import FileResponse
import tempfile
import os
import pandas as pd

router = APIRouter(prefix="/api/test", tags=["Тест"])

@router.get("/simple-excel")
async def simple_excel():
    """Простой тест возврата Excel файла"""
    
    # Создаем временный файл
    temp_dir = "/app/temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx', dir=temp_dir) as f:
        # Создаем простой Excel
        df = pd.DataFrame({
            'Дата': ['01.09', '02.09', '03.09', '04.09', '05.09']
        })
        df.to_excel(f.name, index=False)
        
        return FileResponse(
            f.name,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename="simple_test.xlsx"
        ) 