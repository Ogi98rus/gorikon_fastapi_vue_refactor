from fastapi import APIRouter, HTTPException, Form, Request, Depends
from fastapi.responses import FileResponse
from typing import List, Optional
from datetime import date
import os
import time
from sqlalchemy.orm import Session

from app.models.schemas import KTPGeneratorRequest, KTPGeneratorResponse, WeekDay
from app.models.database import get_db, User
from app.services.ktp_generator import generate_ktp_excel
from app.services.analytics_service import AnalyticsService
from app.dependencies.auth import get_current_user, get_client_ip, get_user_agent
from app.core.config import settings

# Основной роутер для API v2
router = APIRouter(prefix="/api/ktp", tags=["КТП генератор"])

# Legacy роутер для совместимости
legacy_router = APIRouter(prefix="/api", tags=["КТП генератор (Legacy)"])

@router.post("/generate", response_model=KTPGeneratorResponse)
async def generate_ktp_schedule(
    ktp_request: KTPGeneratorRequest,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Генерация календарно-тематического планирования
    
    **Параметры:**
    - `start_date`, `end_date`: Период учебного года
    - `weekdays`: Рабочие дни недели (0=Пн, 1=Вт, ..., 6=Вс)  
    - `lessons_per_day`: Количество уроков по дням недели (7 значений)
    - `holidays`: Праздничные дни в формате ДД.ММ.ГГГГ
    - `vacation`: Каникулы в формате ДД.ММ.ГГГГ
    - `file_name`: Имя выходного файла
    """
    
    start_time = time.time()
    
    try:
        # Валидация дат
        if end_date <= start_date:
            raise HTTPException(
                status_code=400,
                detail="Дата окончания должна быть больше даты начала"
            )
        
        # Валидация рабочих дней
        valid_weekdays = []
        for day in weekdays:
            if 0 <= day <= 6:
                valid_weekdays.append(WeekDay(day))
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Недопустимый день недели: {day}. Разрешены: 0-6"
                )
        
        if not valid_weekdays:
            raise HTTPException(
                status_code=400,
                detail="Необходимо выбрать хотя бы один рабочий день"
            )
        
        # Валидация количества уроков
        if len(lessons_per_day) != 7:
            raise HTTPException(
                status_code=400,
                detail="Необходимо указать количество уроков для каждого дня недели (7 значений)"
            )
        
        for i, lessons in enumerate(lessons_per_day):
            if lessons < 0 or lessons > settings.max_lessons_per_day:
                raise HTTPException(
                    status_code=400,
                    detail=f"Количество уроков в день {i} должно быть от 0 до {settings.max_lessons_per_day}"
                )
        
        # Создаем запрос
        ktp_request = KTPGeneratorRequest(
            start_date=start_date,
            end_date=end_date,
            weekdays=valid_weekdays,
            lessons_per_day=lessons_per_day,
            holidays=holidays,
            vacation=vacation,
            file_name=file_name
        )
        
        # Генерируем Excel
        result = generate_ktp_excel(ktp_request)
        excel_path = f"/app/temp/{result['file_name']}"
        total_lessons = result['total_lessons']
        working_days = result['working_days']
        
        # Получаем размер файла
        file_size = result.get('file_size', 0)
        
        # Формируем имя файла (ASCII-safe)
        safe_file_name = file_name.replace(" ", "_").encode('ascii', 'ignore').decode('ascii')
        filename = f"{safe_file_name}.xlsx"
        
        # Измеряем время обработки
        processing_time = int((time.time() - start_time) * 1000)
        
        # Логируем аналитику
        try:
            AnalyticsService.log_generation(
                db=db,
                user_id=current_user.id if current_user else None,
                generator_type="ktp",
                parameters={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "weekdays": weekdays,
                    "lessons_per_day": lessons_per_day,
                    "holidays_count": len([h for h in holidays if h.strip()]),
                    "vacation_count": len([v for v in vacation if v.strip()]),
                    "file_name": file_name
                },
                file_name=filename,
                original_file_name=filename,
                file_path=excel_path,
                file_size=file_size,
                total_lessons=total_lessons,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                processing_time=processing_time
            )
        except Exception as e:
            # Не прерываем генерацию если аналитика не работает
            print(f"Analytics logging failed: {e}")
        
        # Возвращаем файл
        return FileResponse(
            excel_path,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=filename,
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename}",
                "X-Total-Lessons": str(total_lessons),
                "X-Working-Days": str(working_days),
                "X-File-Size": str(file_size),
                "X-Processing-Time": str(processing_time)
            }
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка генерации Excel: {str(e)}"
        )

# НОВЫЙ простой КТП эндпоинт
@legacy_router.post("/ktp-simple")
async def generate_ktp_simple(
    start_date: str = Form("2025-09-01"),
    end_date: str = Form("2025-09-10"),
    file_name: str = Form("simple_schedule")
):
    """Упрощенный КТП генератор только с основными функциями"""
    
    import tempfile
    import os
    import pandas as pd
    from datetime import date, timedelta
    
    print(f"SIMPLE DEBUG: Начало simple эндпоинта")
    print(f"SIMPLE DEBUG: start_date={start_date}, end_date={end_date}, file_name={file_name}")
    
    try:
        # Парсим даты
        start_dt = date.fromisoformat(start_date)
        end_dt = date.fromisoformat(end_date)
        
        # Генерируем простое расписание только рабочие дни
        dates = []
        current = start_dt
        while current <= end_dt:
            if current.weekday() < 5:  # Пн-Пт
                dates.append(current.strftime('%d.%m'))
            current += timedelta(days=1)
        
        print(f"SIMPLE DEBUG: Сгенерировано {len(dates)} дат")
        
        # Создаем Excel файл
        temp_dir = "/app/temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx', dir=temp_dir) as f:
            df = pd.DataFrame({'Дата': dates})
            df.to_excel(f.name, index=False)
            
            print(f"SIMPLE DEBUG: Excel файл создан: {f.name}")
            
            return FileResponse(
                f.name,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                filename=f"{file_name}.xlsx",
                headers={"Content-Disposition": f"attachment; filename={file_name}.xlsx"}
            )
    
    except Exception as e:
        print(f"SIMPLE ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка: {str(e)}")

# Совместимость со старым API (основной эндпоинт) - УПРОЩЕННАЯ ВЕРСИЯ
@legacy_router.post("/ktp-generator")
async def generate_ktp_legacy(
    start_date: str = Form(...),
    end_date: str = Form(...),
    weekdays: List[int] = Form(...),
    lessons_per_day: List[int] = Form(...),
    holidays: List[str] = Form(default=[]),
    vacation: List[str] = Form(default=[]),
    file_name: str = Form(default="schedule")
):
    """Упрощенная обратная совместимость со старым API"""
    
    import tempfile
    import os
    import pandas as pd
    from datetime import date, timedelta
    
    try:
        # Парсим даты
        start_dt = date.fromisoformat(start_date)
        end_dt = date.fromisoformat(end_date)
        
        if end_dt <= start_dt:
            raise HTTPException(status_code=400, detail="Дата окончания должна быть позже даты начала")
        
        # Генерируем расписание
        schedule_dates = []
        current = start_dt
        
        # Парсим праздники
        holiday_dates = set()
        for holiday in holidays:
            if holiday.strip():
                try:
                    parts = holiday.strip().split('.')
                    if len(parts) == 3:
                        day, month, year = map(int, parts)
                        holiday_dates.add(date(year, month, day))
                except:
                    continue
        
        # Парсим каникулы
        vacation_dates = set()
        for vacation_day in vacation:
            if vacation_day.strip():
                try:
                    parts = vacation_day.strip().split('.')
                    if len(parts) == 3:
                        day, month, year = map(int, parts)
                        vacation_dates.add(date(year, month, day))
                except:
                    continue
        
        # Генерируем рабочие даты
        while current <= end_dt:
            # Проверяем что день входит в рабочие дни
            if current.weekday() in weekdays:
                # Проверяем что это не праздник и не каникулы
                if current not in holiday_dates and current not in vacation_dates:
                    # Добавляем уроки согласно расписанию
                    lessons_count = lessons_per_day[current.weekday()]
                    for _ in range(lessons_count):
                        schedule_dates.append(current.strftime('%d.%m'))
            
            current += timedelta(days=1)
        
        # Убираем дубликаты но сохраняем порядок
        seen = set()
        unique_dates = []
        for date_str in schedule_dates:
            if date_str not in seen:
                unique_dates.append(date_str)
                seen.add(date_str)
        
        # Создаем Excel файл
        temp_dir = "/app/temp"
        os.makedirs(temp_dir, exist_ok=True)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx', dir=temp_dir) as f:
            df = pd.DataFrame({'Дата': unique_dates})
            
            # Используем openpyxl для лучшего форматирования
            with pd.ExcelWriter(f.name, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Расписание')
                
                # Форматируем
                worksheet = writer.sheets['Расписание']
                worksheet.column_dimensions['A'].width = 15
                
                # Центрируем даты
                from openpyxl.styles import Alignment
                alignment = Alignment(horizontal='center')
                for cell in worksheet['A']:
                    cell.alignment = alignment
            
            print(f"DEBUG: XLSX файл создан с {len(unique_dates)} датами, размер: {os.path.getsize(f.name)} байт")
            
            # Возвращаем файл
            return FileResponse(
                f.name,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                filename=f"{file_name}.xlsx",
                headers={
                    "Content-Disposition": f"attachment; filename={file_name}.xlsx"
                }
            )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Ошибка в данных: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации: {str(e)}") 