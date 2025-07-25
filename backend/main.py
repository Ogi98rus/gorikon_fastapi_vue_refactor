from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os
import pandas as pd
import openpyxl
from fpdf import FPDF
from typing import List
import random
import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======= МАТЕМАТИЧЕСКИЕ ПРИМЕРЫ =======
class Example:
    def __init__(self, numcount=2, operator=["+", "-"], interval=[0, 100]):
        if numcount < 2:
            raise ValueError("Требуется два или более числа")
        self.numcount = numcount
        self.operator = operator
        self.interval = interval
        self._numbers_ = []
        self._operators_ = []
        self._result_ = None
        self.generate_problem()
    
    def generate_problem(self):
        while True:
            self._operators_ = [random.choice(self.operator) for _ in range(self.numcount - 1)]
            self._numbers_ = self.generate_smart_numbers()
            self._result_ = self.solve_it()
            if self._result_ > 0:
                break
    
    def generate_smart_numbers(self):
        numbers = []
        
        # Генерируем первое число
        numbers.append(random.randint(self.interval[0], self.interval[1]))
        
        # Генерируем остальные числа с учетом операций
        for i, operator in enumerate(self._operators_):
            if operator == "/":
                # Для деления: генерируем делитель и корректируем предыдущее число
                divisor = random.randint(2, min(20, self.interval[1]))  # Делитель от 2 до 20
                quotient = random.randint(1, self.interval[1] // divisor)  # Результат деления
                
                # Корректируем предыдущее число, чтобы деление было нацело
                if i == 0:
                    numbers[0] = quotient * divisor
                else:
                    # Если это не первая операция, нужно учесть накопленный результат
                    current_result = numbers[0]
                    for j in range(i):
                        if self._operators_[j] == "+":
                            current_result += numbers[j + 1] if j + 1 < len(numbers) else 0
                        elif self._operators_[j] == "-":
                            current_result -= numbers[j + 1] if j + 1 < len(numbers) else 0
                        elif self._operators_[j] == "*":
                            current_result *= numbers[j + 1] if j + 1 < len(numbers) else 1
                    
                    # Подбираем делитель так, чтобы current_result делился нацело
                    if current_result > 0:
                        possible_divisors = [d for d in range(2, min(current_result + 1, 21)) if current_result % d == 0]
                        if possible_divisors:
                            divisor = random.choice(possible_divisors)
                        else:
                            divisor = random.randint(2, min(20, self.interval[1]))
                    else:
                        divisor = random.randint(2, min(20, self.interval[1]))
                
                numbers.append(divisor)
            else:
                # Для остальных операций генерируем обычные числа
                numbers.append(random.randint(self.interval[0], self.interval[1]))
        
        return numbers
    
    def __str__(self):
        problem_str = ""
        for i in range(len(self._operators_)):
            problem_str += f"{self._numbers_[i]} {self._operators_[i]} "
        problem_str += f"{self._numbers_[-1]} = "
        return problem_str
    
    def solve_it(self):
        result = self._numbers_[0]
        for i, operator in enumerate(self._operators_):
            if operator == "+":
                result += self._numbers_[i + 1]
            elif operator == "-":
                result -= self._numbers_[i + 1]
            elif operator == "*":
                result *= self._numbers_[i + 1]
            elif operator == "/":
                if self._numbers_[i + 1] == 0:
                    self._numbers_[i + 1] = random.randint(1, self.interval[1])
                result = result // self._numbers_[i + 1]  # Используем целочисленное деление
        return int(result)
    
    def whole_example(self):
        return f"{self} {self._result_}"

def create_pdf(examples, answers=None, with_answers=False):
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_font('Arial', '', 12)
    for i, example in enumerate(examples):
        if with_answers and answers:
            text = f"{example.strip()} {answers[i].split('=')[-1]}"
            pdf.cell(0, 10, text, ln=True)
        else:
            pdf.cell(0, 10, example, ln=True)
    temp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(temp.name)
    temp.close()
    return temp.name

@app.post("/api/math-generator")
async def math_generator(
    num_operands: int = Form(...),
    operation: List[str] = Form(...),
    interval_start: int = Form(...),
    interval_end: int = Form(...),
    example_count: int = Form(...)
):
    try:
        if num_operands < 2 or example_count < 1:
            raise HTTPException(status_code=400, detail="Некорректные параметры")
        examples = []
        answers = []
        for _ in range(example_count):
            ex = Example(numcount=num_operands, operator=operation, interval=[interval_start, interval_end])
            examples.append(str(ex))
            answers.append(ex.whole_example())
        pdf_path = create_pdf(examples, answers, with_answers=True)
        return FileResponse(pdf_path, filename="worksheet.pdf", media_type="application/pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ======= ГЕНЕРАТОР РАСПИСАНИЯ =======
def generate_schedule(start_date, end_date, weekdays, holidays, vacation, lessons_per_day):
    schedule = []
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() in weekdays:
            if current_date not in holidays and current_date not in vacation:
                for _ in range(lessons_per_day[current_date.weekday()]):
                    schedule.append(current_date)
        current_date += datetime.timedelta(days=1)
    return schedule

@app.post("/api/ktp-generator")
async def ktp_generator(
    start_date: str = Form(...),
    end_date: str = Form(...),
    weekdays: List[int] = Form(...),
    holidays: List[str] = Form([]),
    vacation: List[str] = Form([]),
    lessons_per_day: List[int] = Form(...),
    file_name: str = Form("schedule.xlsx")
):
    try:
        start_date_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        holidays_dt = [datetime.datetime.strptime(d, '%d.%m.%Y').date() for d in holidays if d]
        vacation_dt = [datetime.datetime.strptime(d, '%d.%m.%Y').date() for d in vacation if d]
        lessons_per_day_int = [int(x) for x in lessons_per_day]
        weekdays_int = [int(x) for x in weekdays]
        schedule = generate_schedule(start_date_dt, end_date_dt, weekdays_int, holidays_dt, vacation_dt, lessons_per_day_int)
        df = pd.DataFrame({'Дата': schedule})
        temp = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        writer = pd.ExcelWriter(temp.name, engine='openpyxl')
        df.to_excel(writer, index=False, sheet_name='Schedule')
        workbook = writer.book
        worksheet = writer.sheets['Schedule']
        date_format = openpyxl.styles.NamedStyle(name='date_format')
        date_format.number_format = 'DD.MM'
        date_column = worksheet['A']
        for cell in date_column:
            cell.style = date_format
        workbook.save(temp.name)
        writer.close()
        temp.close()
        return FileResponse(temp.name, filename=f"{file_name}.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 