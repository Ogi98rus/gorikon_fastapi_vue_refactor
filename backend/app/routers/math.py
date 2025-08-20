from fastapi import APIRouter, HTTPException, Form, Request
from fastapi.responses import FileResponse
from typing import List
import os
import time
import random
from fpdf import FPDF

from app.core.config import settings

# Основной роутер для API v2
router = APIRouter(prefix="/api/math", tags=["Математический генератор"])

# Legacy роутер для совместимости
legacy_router = APIRouter(prefix="/api", tags=["Математический генератор (Legacy)"])

class MathPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Math Examples', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

def generate_math_example(num_operands, operations, interval_start, interval_end):
    """Генерирует один математический пример"""
    numbers = [random.randint(interval_start, interval_end) for _ in range(num_operands)]
    ops = random.choices(operations, k=num_operands - 1)
    
    # Формируем пример
    example = str(numbers[0])
    result = numbers[0]
    
    for i, op in enumerate(ops):
        example += f" {op} {numbers[i + 1]}"
        if op == '+':
            result += numbers[i + 1]
        elif op == '-':
            result -= numbers[i + 1]
        elif op == '*':
            result *= numbers[i + 1]
        elif op == '/':
            if numbers[i + 1] != 0:
                result /= numbers[i + 1]
                result = int(result) if result.is_integer() else result
    
    example += f" = {result}"
    return example, result

def generate_math_pdf(num_operands, operations, interval_start, interval_end, example_count):
    """Генерирует PDF с математическими примерами"""
    pdf = MathPDF()
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    
    # Добавляем информацию о параметрах
    pdf.cell(0, 10, f'Generation Parameters:', 0, 1)
    pdf.cell(0, 8, f'- Number of operands: {num_operands}', 0, 1)
    pdf.cell(0, 8, f'- Operations: {", ".join(operations)}', 0, 1)
    pdf.cell(0, 8, f'- Number range: from {interval_start} to {interval_end}', 0, 1)
    pdf.cell(0, 8, f'- Number of examples: {example_count}', 0, 1)
    pdf.ln(10)
    
    # Генерируем примеры
    examples = []
    answers = []
    
    for i in range(example_count):
        example, answer = generate_math_example(num_operands, operations, interval_start, interval_end)
        examples.append(example)
        answers.append(answer)
    
    # Первая страница с примерами
    pdf.cell(0, 10, 'Examples:', 0, 1, 'C')
    pdf.ln(5)
    
    for i, example in enumerate(examples, 1):
        pdf.cell(0, 8, f'{i:2d}. {example}', 0, 1)
        if i % 20 == 0 and i < example_count:
            pdf.add_page()
            pdf.cell(0, 10, 'Examples (continued):', 0, 1, 'C')
            pdf.ln(5)
    
    # Страница с ответами
    pdf.add_page()
    pdf.cell(0, 10, 'Answers:', 0, 1, 'C')
    pdf.ln(5)
    
    for i, answer in enumerate(answers, 1):
        pdf.cell(0, 8, f'{i:2d}. {answer}', 0, 1)
        if i % 20 == 0 and i < example_count:
            pdf.add_page()
            pdf.cell(0, 10, 'Answers (continued):', 0, 1, 'C')
            pdf.ln(5)
    
    # Сохраняем файл
    filename = f"math_examples_{example_count}.pdf"
    filepath = os.path.join(settings.temp_dir, filename)
    pdf.output(filepath)
    
    return filepath

@router.post("/generate")
async def generate_math_problems(
    request: Request,
    num_operands: int = Form(2, ge=2, le=settings.max_operands),
    operations: List[str] = Form(..., alias="operations"),
    interval_start: int = Form(0, ge=settings.min_interval, le=settings.max_interval),
    interval_end: int = Form(100, ge=settings.min_interval, le=settings.max_interval),
    example_count: int = Form(10, ge=1, le=settings.max_examples)
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
        valid_operations = ['+', '-', '*', '/']
        filtered_operations = [op for op in operations if op in valid_operations]
        
        if not filtered_operations:
            raise HTTPException(
                status_code=400,
                detail="Необходимо выбрать хотя бы одну операцию из: +, -, *, /"
            )
        
        # Генерируем PDF
        pdf_path = generate_math_pdf(
            num_operands, 
            filtered_operations, 
            interval_start, 
            interval_end, 
            example_count
        )
        
        # Формируем имя файла
        filename = f"math_examples_{example_count}.pdf"
        
        # Измеряем время обработки
        processing_time = int((time.time() - start_time) * 1000)
        
        # Возвращаем файл
        return FileResponse(
            pdf_path,
            media_type='application/pdf',
            filename=filename,
            headers={
                'X-Processing-Time': str(processing_time),
                'X-Examples-Count': str(example_count)
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
    example_count: int = Form(10, ge=1, le=100)
):
    """Legacy endpoint для совместимости"""
    return await generate_math_problems(
        request, num_operands, operations, 
        interval_start, interval_end, example_count
    ) 