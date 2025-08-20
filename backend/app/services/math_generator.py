import random
import tempfile
import os
from fpdf import FPDF
from datetime import datetime
from typing import List, Tuple
from app.models.schemas import MathGeneratorRequest, MathOperation
from app.core.config import settings

# Настройки страницы
CELL_SIZE = 5  # Размер клетки в миллиметрах (как в тетрадях)
MARGIN = 10    # Отступ от края страницы в мм
MARGIN_TOP = 40  # Верхний отступ с учетом заголовка
MARGIN_LEFT = 15  # Левый отступ для примеров
EXAMPLE_HEIGHT = 8  # Высота строки для примера

# ТОЧНЫЕ РАСЧЕТЫ для размещения:
# Номер примера: MARGIN (10мм) + ширина номера (20мм) = 30мм
# Пример начинается: 30мм + отступ (5мм) = 35мм
NUMBER_WIDTH = 20  # Ширина колонки с номером
NUMBER_TO_EXAMPLE_GAP = 5  # Отступ между номером и примером

class MathGridPDF(FPDF):
    """Класс PDF с сеткой для математических примеров"""
    
    def __init__(self, subject="Математика"):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.subject = subject
        self.add_page()
        
        # Пытаемся использовать доступные шрифты
        try:
            # Пробуем Helvetica (стандартный шрифт PDF)
            self.set_font("Helvetica", "B", 16)
        except:
            try:
                # Fallback на Arial
                self.set_font("Arial", "B", 16)
            except:
                # Последний fallback на Times
                self.set_font("Times", "B", 16)
        
    def draw_header(self):
        """Рисуем заголовок страницы"""
        # Устанавливаем позицию для заголовка
        self.set_y(10)
        
        # Используем безопасные шрифты
        try:
            self.set_font("Helvetica", "B", 14)
        except:
            try:
                self.set_font("Arial", "B", 14)
            except:
                self.set_font("Times", "B", 14)
        
        # Заголовок на английском для совместимости
        self.cell(0, 8, "Math Worksheet", 0, 1, "C")
        
        # Добавляем строку для ФИО
        try:
            self.set_font("Helvetica", "", 12)
        except:
            try:
                self.set_font("Arial", "", 12)
            except:
                self.set_font("Times", "", 12)
        
        self.cell(0, 10, "Name: _________________________", 0, 1, "L")
        
        # Добавляем дату
        try:
            self.set_font("Helvetica", "", 10)
        except:
            try:
                self.set_font("Arial", "", 10)
            except:
                self.set_font("Times", "", 10)
        
        date_str = datetime.now().strftime("%d.%m.%Y")
        self.cell(0, 8, f"Date: {date_str}", 0, 1, "L")
        
        # Добавляем дополнительное пространство после заголовка
        self.ln(5)
    
    def draw_grid(self):
        """Рисуем сетку на странице"""
        # Рассчитываем рабочую область (без отступов)
        width = self.w - 2 * MARGIN
        height = self.h - MARGIN_TOP - MARGIN
        
        # Устанавливаем серый цвет для линий
        self.set_draw_color(200)
        
        # Рисуем горизонтальные линии
        for y in range(0, int(height) + 1, CELL_SIZE):
            # Каждую 5-ю линию делаем чуть темнее
            if y % (5 * CELL_SIZE) == 0:
                self.set_draw_color(150)
                self.set_line_width(0.25)
            else:
                self.set_draw_color(200)
                self.set_line_width(0.1)
            self.line(MARGIN, MARGIN_TOP + y, MARGIN + width, MARGIN_TOP + y)
            
        # Рисуем вертикальные линии
        for x in range(0, int(width) + 1, CELL_SIZE):
            # Каждую 5-ю линию делаем чуть темнее
            if x % (5 * CELL_SIZE) == 0:
                self.set_draw_color(150)
                self.set_line_width(0.25)
            else:
                self.set_draw_color(200)
                self.set_line_width(0.1)
            self.line(MARGIN + x, MARGIN_TOP, MARGIN + x, MARGIN_TOP + height)
    
    def add_examples_to_grid(self, examples: List[str]):
        """Добавляем примеры в сетку"""
        # Используем безопасные шрифты
        try:
            self.set_font("Helvetica", "", 9)
        except:
            try:
                self.set_font("Arial", "", 9)
            except:
                self.set_font("Times", "", 9)
        
        # ТОЧНЫЕ РАСЧЕТЫ для сетки 5x5мм:
        # MARGIN_TOP = 40мм (начало сетки)
        # CELL_SIZE = 5мм (размер ячейки)
        # Первая строка примеров начинается в центре первой ячейки сетки
        start_y = MARGIN_TOP + (CELL_SIZE // 2)  # 40 + 2.5 = 42.5мм
        
        for i, example in enumerate(examples):
            # Вычисляем позицию Y для каждой строки
            # Каждый пример размещается в центре своей ячейки сетки
            example_y = start_y + (i * CELL_SIZE)
            
            # Проверяем, не выходит ли пример за пределы страницы
            if example_y > self.h - MARGIN - 10:
                # Добавляем новую страницу
                self.add_page()
                self.draw_grid()
                # Сбрасываем позицию для новой страницы
                start_y = MARGIN_TOP + (CELL_SIZE // 2)
                example_y = start_y + (i * CELL_SIZE)
            
            # Размещаем пример точно по центру ячейки сетки
            # Номер примера (левый край + отступ)
            self.set_xy(MARGIN, example_y - 3)  # -3 для центрирования по вертикали
            self.cell(NUMBER_WIDTH, 6, f"{i+1}.", 0, 0, "L")
            
            # Пример (номер + отступ)
            self.set_xy(MARGIN + NUMBER_WIDTH + NUMBER_TO_EXAMPLE_GAP, example_y - 3)
            self.cell(0, 6, f"{example} =", 0, 1, "L")

class Example:
    """Класс для генерации математического примера (как в оригинале)"""
    
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
        problem_str += f"{self._numbers_[-1]}"  # Убираем знак = из базового примера
        return problem_str.rstrip()  # Убираем лишние пробелы в конце
    
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

def create_pdf_with_grid(examples: List[str], subject: str = "Математика") -> str:
    """Создание PDF файла с сеткой для математических примеров (для учеников)"""
    try:
        print(f"Создание PDF с сеткой для {len(examples)} примеров")
        
        # Создаем PDF с сеткой
        pdf = MathGridPDF(subject=subject)
        
        # Рисуем заголовок и сетку на первой странице
        pdf.draw_header()
        pdf.draw_grid()
        
        # Добавляем примеры в сетку
        pdf.add_examples_to_grid(examples)
        
        # Создаем временный файл в безопасной директории
        temp_dir = settings.temp_dir
        os.makedirs(temp_dir, exist_ok=True)
        
        temp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir=temp_dir)
        pdf.output(temp.name)
        temp.close()
        
        # Проверяем размер файла
        file_size = os.path.getsize(temp.name)
        print(f"PDF создан: {temp.name}, размер: {file_size} байт")
        
        if file_size < 1000:  # Если файл слишком маленький
            print("ВНИМАНИЕ: PDF файл слишком маленький, возможно есть проблема")
        
        return temp.name
        
    except Exception as e:
        print(f"Ошибка создания PDF с сеткой: {e}")
        
        # Fallback: создаем простой текстовый файл
        temp_dir = settings.temp_dir
        os.makedirs(temp_dir, exist_ok=True)
        
        temp = tempfile.NamedTemporaryFile(delete=False, suffix='.txt', dir=temp_dir, mode='w', encoding='utf-8')
        temp.write(f"Ошибка создания PDF: {str(e)}\n")
        temp.write("Примеры математических заданий:\n")
        
        for i, example in enumerate(examples):
            temp.write(f"{i+1}. {example}\n")
        
        temp.close()
        return temp.name

def create_pdf_for_teacher(examples: List[str], answers: List[str], subject: str = "Математика") -> str:
    """Создание PDF файла с ответами для учителя"""
    try:
        pdf = MathGridPDF(subject=subject)
        
        # Рисуем заголовок и сетку на первой странице
        pdf.draw_header()
        pdf.draw_grid()
        
        # Добавляем примеры с ответами
        # ТОЧНЫЕ РАСЧЕТЫ для сетки 5x5мм:
        # MARGIN_TOP = 40мм (начало сетки)
        # CELL_SIZE = 5мм (размер ячейки)
        # Первая строка примеров начинается в центре первой ячейки сетки
        start_y = MARGIN_TOP + (CELL_SIZE // 2)  # 40 + 2.5 = 42.5мм
        
        for i, (example, answer) in enumerate(zip(examples, answers)):
            # Вычисляем позицию Y для каждой строки
            # Каждый пример размещается в центре своей ячейки сетки
            example_y = start_y + (i * CELL_SIZE)
            
            # Проверяем, не выходит ли пример за пределы страницы
            if example_y > pdf.h - MARGIN - 10:
                # Добавляем новую страницу
                pdf.add_page()
                pdf.draw_grid()
                # Сбрасываем позицию для новой страницы
                start_y = MARGIN_TOP + (CELL_SIZE // 2)
                example_y = start_y + (i * CELL_SIZE)
            
            # Размещаем пример точно по центру ячейки сетки
            # Номер примера (левый край + отступ)
            pdf.set_xy(MARGIN, example_y - 3)  # -3 для центрирования по вертикали
            pdf.cell(NUMBER_WIDTH, 6, f"{i+1}.", 0, 0, "L")
            
            # Пример с ответом (номер + отступ)
            pdf.set_xy(MARGIN + NUMBER_WIDTH + NUMBER_TO_EXAMPLE_GAP, example_y - 3)
            pdf.cell(0, 6, f"{example} = {answer}", 0, 1, "L")
        
        # Создаем временный файл в безопасной директории
        temp_dir = settings.temp_dir
        os.makedirs(temp_dir, exist_ok=True)
        
        temp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir=temp_dir)
        pdf.output(temp.name)
        temp.close()
        return temp.name
        
    except Exception as e:
        print(f"Ошибка создания PDF для учителя: {e}")
        
        # Fallback: создаем простой текстовый файл
        temp_dir = settings.temp_dir
        os.makedirs(temp_dir, exist_ok=True)
        
        temp = tempfile.NamedTemporaryFile(delete=False, suffix='.txt', dir=temp_dir, mode='w', encoding='utf-8')
        temp.write(f"Ошибка создания PDF: {str(e)}\n")
        temp.write("Примеры математических заданий с ответами:\n")
        
        for i, (example, answer) in enumerate(zip(examples, answers)):
            temp.write(f"{i+1}. {example} = {answer}\n")
        
        temp.close()
        return temp.name

def generate_math_examples(request: MathGeneratorRequest) -> Tuple[List[str], List[str]]:
    """Генерация математических примеров (один раз для обоих вариантов)"""
    try:
        print(f"Генерация примеров: {request.example_count} примеров")
        
        # Преобразуем операции в строки
        operator_strings = [op.value for op in request.operations]
        print(f"Операции: {operator_strings}")
        
        # Создаем примеры ОДИН РАЗ
        examples = []
        answers = []
        
        for i in range(request.example_count):
            ex = Example(
                numcount=request.num_operands,
                operator=operator_strings,
                interval=[request.interval_start, request.interval_end]
            )
            examples.append(str(ex))
            answers.append(str(ex._result_))
            print(f"Пример {i+1}: {str(ex)} = {ex._result_}")
        
        print(f"Сгенерировано {len(examples)} примеров")
        return examples, answers
        
    except Exception as e:
        print(f"Ошибка генерации примеров: {e}")
        raise e

# Основная функция сервиса
def generate_math_pdf(request: MathGeneratorRequest, for_teacher: bool = False) -> str:
    """Генерация PDF с математическими примерами"""
    
    try:
        print(f"Генерация PDF: {request.example_count} примеров, для учителя: {for_teacher}")
        
        # Генерируем примеры ОДИН РАЗ
        examples, answers = generate_math_examples(request)
        
        if for_teacher:
            # Создаем PDF с ответами для учителя
            pdf_path = create_pdf_for_teacher(examples, answers, subject="Математика")
        else:
            # Создаем PDF с сеткой для учеников (без ответов)
            pdf_path = create_pdf_with_grid(examples, subject="Математика")
        
        print(f"PDF создан: {pdf_path}")
        return pdf_path
        
    except Exception as e:
        # Логируем ошибку и создаем простой файл
        print(f"Ошибка генерации математических примеров: {e}")
        
        # Создаем простой текстовый файл как fallback
        temp_dir = settings.temp_dir
        os.makedirs(temp_dir, exist_ok=True)
        
        temp = tempfile.NamedTemporaryFile(delete=False, suffix='.txt', dir=temp_dir, mode='w', encoding='utf-8')
        temp.write(f"Ошибка генерации: {str(e)}\n")
        temp.write("Примеры математических заданий:\n")
        
        for i in range(min(request.example_count, 10)):
            if for_teacher:
                temp.write(f"{i+1}. 2 + 3 = 5\n")
            else:
                temp.write(f"{i+1}. 2 + 2 = ___\n")
        
        temp.close()
        return temp.name 

def generate_both_math_pdfs(request: MathGeneratorRequest) -> Tuple[str, str]:
    """Генерация обоих вариантов PDF с одинаковыми примерами"""
    try:
        print(f"Генерация ОБОИХ вариантов PDF: {request.example_count} примеров")
        
        # Генерируем примеры ОДИН РАЗ
        examples, answers = generate_math_examples(request)
        
        # Создаем PDF для ученика (сетка без ответов)
        student_pdf = create_pdf_with_grid(examples, subject="Математика")
        
        # Создаем PDF для учителя (с ответами)
        teacher_pdf = create_pdf_for_teacher(examples, answers, subject="Математика")
        
        print(f"Оба PDF созданы: ученик - {student_pdf}, учитель - {teacher_pdf}")
        return student_pdf, teacher_pdf
        
    except Exception as e:
        print(f"Ошибка генерации обоих PDF: {e}")
        raise e 