import random
import tempfile
import os
from fpdf import FPDF
from typing import List, Tuple
from app.models.schemas import MathGeneratorRequest, MathOperation
from app.core.config import settings

class MathPDF(FPDF):
    """Расширенный класс PDF с поддержкой кириллицы"""
    
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        # Добавляем шрифт с поддержкой кириллицы
        try:
            self.add_font('DejaVu', '', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', uni=True)
            self.add_font('DejaVu', 'B', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', uni=True)
        except:
            # Fallback на стандартный шрифт
            pass

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
    """Создание PDF файла (как в оригинале)"""
    try:
        pdf = MathPDF()
        pdf.add_page()
        
        # Пытаемся использовать кириллический шрифт, если недоступен - используем стандартный
        try:
            pdf.set_font('DejaVu', '', 12)
        except:
            pdf.set_font('Arial', '', 12)
        
        for i, example in enumerate(examples):
            if with_answers and answers:
                text = f"{example.strip()} {answers[i].split('=')[-1]}"
                pdf.cell(0, 10, text, ln=True)
            else:
                pdf.cell(0, 10, example, ln=True)
        
        # Создаем временный файл в безопасной директории
        temp_dir = settings.temp_dir
        os.makedirs(temp_dir, exist_ok=True)
        
        temp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir=temp_dir)
        pdf.output(temp.name)
        temp.close()
        return temp.name
        
    except Exception as e:
        # Если PDF не работает, создаем простой текстовый файл
        temp_dir = settings.temp_dir
        os.makedirs(temp_dir, exist_ok=True)
        
        temp = tempfile.NamedTemporaryFile(delete=False, suffix='.txt', dir=temp_dir, mode='w', encoding='utf-8')
        
        for i, example in enumerate(examples):
            if with_answers and answers:
                text = f"{example.strip()} {answers[i].split('=')[-1]}\n"
                temp.write(text)
            else:
                temp.write(f"{example}\n")
        
        temp.close()
        return temp.name

# Основная функция сервиса
def generate_math_pdf(request: MathGeneratorRequest) -> str:
    """Генерация PDF с математическими примерами (упрощенная версия)"""
    
    try:
        # Преобразуем операции в строки
        operator_strings = [op.value for op in request.operations]
        
        # Создаем примеры
        examples = []
        answers = []
        
        for _ in range(request.example_count):
            ex = Example(
                numcount=request.num_operands,
                operator=operator_strings,
                interval=[request.interval_start, request.interval_end]
            )
            examples.append(str(ex))
            answers.append(ex.whole_example())
        
        # Создаем PDF с ответами (как в оригинале)
        pdf_path = create_pdf(examples, answers, with_answers=True)
        
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
            temp.write(f"{i+1}. 2 + 3 = 5\n")
        
        temp.close()
        return temp.name 