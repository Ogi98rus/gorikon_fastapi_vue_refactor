from fastapi import APIRouter, HTTPException, Form, Request
from fastapi.responses import FileResponse
from typing import List
import os
import time
from app.services.math_generator import generate_math_pdf
from app.models.schemas import MathGeneratorRequest, MathOperation
from app.core.config import settings

# Основной роутер для API v2
router = APIRouter(prefix="/api/math", tags=["Математический генератор"])

# Legacy роутер для совместимости
legacy_router = APIRouter(prefix="/api", tags=["Математический генератор (Legacy)"])

@router.post("/generate")
async def generate_math_problems(
    request: Request,
    num_operands: int = Form(2, ge=2, le=10),
    operations: List[str] = Form(..., alias="operations"),
    interval_start: int = Form(0, ge=-1000, le=1000),
    interval_end: int = Form(100, ge=-1000, le=1000),
    example_count: int = Form(10, ge=1, le=100),
    for_teacher: bool = Form(False)
):
    """
    Генерация математических примеров
    
    **Параметры:**
    - `num_operands`: Количество операндов в примере (2-10)
    - `operations`: Операции (+, -, *, /)
    - `interval_start`: Начало диапазона чисел
    - `interval_end`: Конец диапазона чисел  
    - `example_count`: Количество примеров (1-100)
    - `for_teacher`: True - для учителя (с ответами), False - для ученика (без ответов, в сетке)
    """
    
    start_time = time.time()
    
    try:
        # Валидация операций
        valid_operations = ['+', '-', '*', '/']
        filtered_operations = [op for op in operations if op in valid_operations]
        
        if not filtered_operations:
            raise HTTPException(
                status_code=400,
                detail="Необходимо выбрать хотя бы одну операцию из: +, -, *, /"
            )
        
        # Создаем объект запроса
        math_request = MathGeneratorRequest(
            num_operands=num_operands,
            operations=[MathOperation(value=op) for op in filtered_operations],
            interval_start=interval_start,
            interval_end=interval_end,
            example_count=example_count
        )
        
        # Генерируем PDF
        pdf_path = generate_math_pdf(math_request, for_teacher=for_teacher)
        
        # Формируем имя файла
        variant = "teacher" if for_teacher else "student"
        filename = f"math_examples_{example_count}_{variant}.pdf"
        
        # Измеряем время обработки
        processing_time = int((time.time() - start_time) * 1000)
        
        # Возвращаем файл
        return FileResponse(
            pdf_path,
            media_type='application/pdf',
            filename=filename,
            headers={
                'X-Processing-Time': str(processing_time),
                'X-Examples-Count': str(example_count),
                'X-Variant': variant
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка генерации PDF: {str(e)}"
        )

# Legacy endpoint
@legacy_router.post("/math-generator")
async def legacy_math_generator(
    request: Request,
    num_operands: int = Form(2, ge=2, le=10),
    operations: List[str] = Form(..., alias="operations"),
    interval_start: int = Form(0, ge=-1000, le=1000),
    interval_end: int = Form(100, ge=-1000, le=1000),
    example_count: int = Form(10, ge=1, le=100),
    for_teacher: bool = Form(False)
):
    """Legacy endpoint для совместимости"""
    return await generate_math_problems(
        request, num_operands, operations, 
        interval_start, interval_end, example_count, for_teacher
    ) 