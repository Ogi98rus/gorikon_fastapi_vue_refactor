from fastapi import APIRouter, HTTPException, Form, Request, Depends
from fastapi.responses import FileResponse
from typing import List, Optional
import os
import time
from sqlalchemy.orm import Session

from app.models.schemas import MathGeneratorRequest, MathGeneratorResponse, MathOperation
from app.models.database import get_db, User
from app.services.math_generator import generate_math_pdf
from app.services.analytics_service import AnalyticsService
from app.dependencies.auth import get_current_user, get_client_ip, get_user_agent
from app.core.config import settings

# Основной роутер для API v2
router = APIRouter(prefix="/api/math", tags=["Математический генератор"])

# Legacy роутер для совместимости
legacy_router = APIRouter(prefix="/api", tags=["Математический генератор (Legacy)"])

@router.post("/generate", response_model=MathGeneratorResponse)
async def generate_math_problems(
    request: Request,
    # Основные параметры (только исходные)
    num_operands: int = Form(2, ge=2, le=settings.max_operands),
    operations: List[str] = Form(...),
    interval_start: int = Form(0, ge=settings.min_interval, le=settings.max_interval),
    interval_end: int = Form(100, ge=settings.min_interval, le=settings.max_interval),
    example_count: int = Form(10, ge=1, le=settings.max_examples),
    # Зависимости
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Генерация математических примеров
    
    **Параметры:**
    - `num_operands`: Количество операндов в примере (2-10)
    - `operations`: Операции (+, -, *, /)
    - `interval_start`: Начало диапазона чисел
    - `interval_end`: Конец диапазона чисел  
    - `example_count`: Количество примеров (1-1000)
    """
    
    start_time = time.time()
    
    try:
        # Валидация операций
        valid_operations = []
        for op in operations:
            try:
                valid_operations.append(MathOperation(op))
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Недопустимая операция: {op}. Разрешены: +, -, *, /"
                )
        
        if not valid_operations:
            raise HTTPException(
                status_code=400,
                detail="Необходимо выбрать хотя бы одну операцию"
            )
        
        # Создаем запрос
        math_request = MathGeneratorRequest(
            num_operands=num_operands,
            operations=valid_operations,
            interval_start=interval_start,
            interval_end=interval_end,
            example_count=example_count
        )
        
        # Генерируем PDF
        pdf_path = generate_math_pdf(math_request)
        
        # Получаем размер файла
        file_size = os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0
        
        # Формируем имя файла
        filename = f"math_examples_{example_count}.pdf"
        
        # Измеряем время обработки
        processing_time = int((time.time() - start_time) * 1000)
        
        # Логируем аналитику
        try:
            AnalyticsService.log_generation(
                db=db,
                user_id=current_user.id if current_user else None,
                generator_type="math",
                parameters={
                    "num_operands": num_operands,
                    "operations": [op.value for op in valid_operations],
                    "interval_start": interval_start,
                    "interval_end": interval_end,
                    "example_count": example_count
                },
                file_name=filename,
                original_file_name=filename,
                file_path=pdf_path,
                file_size=file_size,
                examples_generated=example_count,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                processing_time=processing_time
            )
        except Exception as e:
            # Не прерываем генерацию если аналитика не работает
            print(f"Analytics logging failed: {e}")
        
        # Возвращаем файл
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=filename,
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename}",
                "X-Examples-Generated": str(example_count),
                "X-File-Size": str(file_size),
                "X-Processing-Time": str(processing_time)
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка генерации PDF: {str(e)}"
        )

# Совместимость со старым API (основной эндпоинт)
@legacy_router.post("/math-generator")
async def generate_math_legacy(
    request: Request,
    num_operands: int = Form(...),
    operation: List[str] = Form(...),
    interval_start: int = Form(...),
    interval_end: int = Form(...),
    example_count: int = Form(...),
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обратная совместимость со старым API"""
    return await generate_math_problems(
        request=request,
        num_operands=num_operands,
        operations=operation,
        interval_start=interval_start,
        interval_end=interval_end,
        example_count=example_count,
        current_user=current_user,
        db=db
    ) 