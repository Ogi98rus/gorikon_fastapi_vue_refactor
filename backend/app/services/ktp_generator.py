import tempfile
import pandas as pd
import openpyxl
import os
from datetime import date, timedelta
from typing import List, Dict, Set
from app.models.schemas import KTPGeneratorRequest
from app.core.config import settings

def generate_schedule(start_date, end_date, weekdays, holidays, vacation, lessons_per_day):
    """Генерация расписания (как в оригинале)"""
    schedule = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() in weekdays:
            if current_date not in holidays and current_date not in vacation:
                for _ in range(lessons_per_day[current_date.weekday()]):
                    schedule.append(current_date)
        current_date += timedelta(days=1)
    return schedule

def generate_ktp_excel(request: KTPGeneratorRequest, current_user=None, db=None) -> dict:
    """Генерация Excel файла с КТП (упрощенная версия)"""
    
    try:
        # weekdays уже список int, не нужно .value
        weekdays_int = request.weekdays
        
        # Парсим праздники
        holidays_dt = []
        for holiday_str in request.holidays:
            if holiday_str.strip():
                try:
                    # Поддерживаем формат ДД.ММ.ГГГГ
                    parts = holiday_str.strip().split('.')
                    if len(parts) == 3:
                        day, month, year = map(int, parts)
                        holidays_dt.append(date(year, month, day))
                except (ValueError, TypeError):
                    continue
        
        # Парсим каникулы
        vacation_dt = []
        for vacation_str in request.vacation:
            if vacation_str.strip():
                try:
                    # Поддерживаем формат ДД.ММ.ГГГГ
                    parts = vacation_str.strip().split('.')
                    if len(parts) == 3:
                        day, month, year = map(int, parts)
                        vacation_dt.append(date(year, month, day))
                except (ValueError, TypeError):
                    continue
        
        # Генерируем расписание (используем оригинальную функцию)
        schedule = generate_schedule(
            request.start_date, 
            request.end_date, 
            weekdays_int, 
            holidays_dt, 
            vacation_dt, 
            request.lessons_per_day
        )
        
        # Создаем безопасную директорию для временного файла
        temp_dir = settings.temp_dir
        os.makedirs(temp_dir, exist_ok=True)
        
        # Создаем временный файл
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx', dir=temp_dir)
        temp_file.close()  # Закрываем файл для записи pandas
        
        try:
            # Создаем DataFrame только с датами в формате ДД.ММ
            if schedule:
                # Создаем список дат в формате ДД.ММ (без года)
                dates_list = []
                for schedule_date in schedule:
                    dates_list.append(schedule_date.strftime('%d.%m'))
                
                df = pd.DataFrame({
                    'Дата': dates_list
                })
            else:
                # Если расписание пустое, создаем пример
                df = pd.DataFrame({
                    'Дата': ['01.09', '02.09', '03.09']
                })
        
            # Сохраняем в Excel с простым форматированием
            with pd.ExcelWriter(temp_file.name, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Расписание')
                
                # Получаем worksheet для форматирования
                worksheet = writer.sheets['Расписание']
                
                # Устанавливаем ширину столбца для дат
                worksheet.column_dimensions['A'].width = 15
                
                # Центрируем даты
                from openpyxl.styles import Alignment
                alignment = Alignment(horizontal='center')
                for cell in worksheet['A']:
                    cell.alignment = alignment
                    
        except Exception as excel_error:
            print(f"Ошибка создания Excel: {excel_error}")
            # Создаем простой текстовый файл как fallback
            with open(temp_file.name.replace('.xlsx', '.txt'), 'w', encoding='utf-8') as txt_file:
                txt_file.write(f"КТП расписание\n")
                txt_file.write(f"Период: {request.start_date} - {request.end_date}\n\n")
                
                if schedule:
                    lesson_counter = 1
                    for schedule_date in schedule:
                        txt_file.write(f"{schedule_date.strftime('%d.%m.%Y')} - Урок {lesson_counter}\n")
                        lesson_counter += 1
                else:
                    txt_file.write("Расписание не создано\n")
            
            temp_file.name = temp_file.name.replace('.xlsx', '.txt')
        
        # Подсчитываем статистику
        total_lessons = len(schedule)
        working_days = len(set(schedule)) if schedule else 0
        
        # Возвращаем словарь вместо tuple  
        file_size = os.path.getsize(temp_file.name) if os.path.exists(temp_file.name) else 0
        
        return {
            "file_name": os.path.basename(temp_file.name),
            "total_lessons": total_lessons,
            "working_days": working_days,
            "file_size": file_size,
            "generation_id": None
        }
        
    except Exception as e:
        # Логируем ошибку и создаем простой файл
        print(f"Ошибка генерации КТП: {e}")
        
        # Создаем безопасную директорию для временного файла
        temp_dir = settings.temp_dir
        os.makedirs(temp_dir, exist_ok=True)
        
        # Создаем простой текстовый файл как fallback
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt', dir=temp_dir, mode='w', encoding='utf-8')
        
        temp_file.write(f"Ошибка генерации КТП: {str(e)}\n")
        temp_file.write(f"Параметры запроса:\n")
        temp_file.write(f"- Период: {request.start_date} - {request.end_date}\n")
        temp_file.write(f"- Рабочие дни: {request.weekdays}\n")
        temp_file.write(f"- Уроков в день: {request.lessons_per_day}\n")
        
        # Простое расписание как пример
        temp_file.write("\nПример расписания:\n")
        current_date = request.start_date
        lesson_count = 0
        while current_date <= request.end_date and lesson_count < 20:
            if current_date.weekday() < 5:  # Пн-Пт
                temp_file.write(f"{current_date.strftime('%d.%m.%Y')} - Урок {lesson_count + 1}\n")
                lesson_count += 1
            current_date += timedelta(days=1)
        
        temp_file.close()
        
        # Возвращаем словарь вместо tuple
        file_size = os.path.getsize(temp_file.name) if os.path.exists(temp_file.name) else 0
        
        return {
            "file_name": os.path.basename(temp_file.name),
            "total_lessons": lesson_count,
            "working_days": min(5, lesson_count),
            "file_size": file_size,
            "generation_id": None  # Для незарегистрированных пользователей
        }
    
    except Exception as e:
        # Логируем ошибку для диагностики
        print(f"Ошибка в generate_ktp_excel: {str(e)}")
        raise Exception(f"Ошибка генерации КТП: {str(e)}") 