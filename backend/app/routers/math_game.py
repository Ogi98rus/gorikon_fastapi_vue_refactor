from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import random
import time
from enum import Enum

router = APIRouter(prefix="/api/math-game", tags=["Math Game"])

class OperationType(str, Enum):
    ADDITION = "addition"
    SUBTRACTION = "subtraction"
    MULTIPLICATION = "multiplication"
    DIVISION = "division"

class GameSettings(BaseModel):
    operations: List[OperationType] = Field(..., description="Типы операций для игры")
    min_number: int = Field(1, ge=1, le=100, description="Минимальное число")
    max_number: int = Field(20, ge=1, le=1000, description="Максимальное число")
    examples_count: int = Field(10, ge=5, le=50, description="Количество примеров")
    time_limit: Optional[int] = Field(None, ge=10, le=300, description="Время на ответ в секундах")

class MathExample(BaseModel):
    question: str
    correct_answer: int
    options: List[int]
    operation: str

class GameSession(BaseModel):
    session_id: str
    examples: List[MathExample]
    settings: GameSettings
    current_example: int = 0
    correct_answers: int = 0
    start_time: float
    end_time: Optional[float] = None

class GameResult(BaseModel):
    session_id: str
    total_examples: int
    correct_answers: int
    score: int  # 1-5 баллов
    time_spent: float
    percentage: float

# Хранилище активных игровых сессий (в продакшене использовать Redis)
active_sessions = {}

def generate_math_example(operation: OperationType, min_num: int, max_num: int) -> MathExample:
    """Генерирует математический пример с 4 вариантами ответа"""
    
    if operation == OperationType.ADDITION:
        a = random.randint(min_num, max_num)
        b = random.randint(min_num, max_num)
        correct = a + b
        question = f"{a} + {b} = ?"
        operation_name = "сложение"
        
    elif operation == OperationType.SUBTRACTION:
        a = random.randint(min_num, max_num)
        b = random.randint(min_num, a)  # b <= a для положительного результата
        correct = a - b
        question = f"{a} - {b} = ?"
        operation_name = "вычитание"
        
    elif operation == OperationType.MULTIPLICATION:
        a = random.randint(min_num, min(max_num, 20))  # Ограничиваем для умножения
        b = random.randint(min_num, min(max_num, 20))
        correct = a * b
        question = f"{a} × {b} = ?"
        operation_name = "умножение"
        
    elif operation == OperationType.DIVISION:
        # Генерируем делимое как произведение двух чисел
        b = random.randint(min_num, min(max_num, 12))
        a = b * random.randint(min_num, min(max_num, 10))
        correct = a // b
        question = f"{a} ÷ {b} = ?"
        operation_name = "деление"
    
    # Генерируем неправильные варианты ответа
    options = [correct]
    while len(options) < 4:
        # Создаем варианты близкие к правильному ответу
        if operation == OperationType.ADDITION:
            wrong = correct + random.randint(-5, 5)
        elif operation == OperationType.SUBTRACTION:
            wrong = correct + random.randint(-5, 5)
        elif operation == OperationType.MULTIPLICATION:
            wrong = correct + random.randint(-10, 10)
        elif operation == OperationType.DIVISION:
            wrong = correct + random.randint(-3, 3)
        
        # Убеждаемся что вариант неправильный и положительный
        if wrong != correct and wrong > 0 and wrong not in options:
            options.append(wrong)
    
    # Перемешиваем варианты ответа
    random.shuffle(options)
    
    return MathExample(
        question=question,
        correct_answer=correct,
        options=options,
        operation=operation_name
    )

def calculate_score(correct: int, total: int) -> int:
    """Вычисляет оценку по 5-балльной системе"""
    percentage = (correct / total) * 100
    
    if percentage >= 90:
        return 5
    elif percentage >= 75:
        return 4
    elif percentage >= 60:
        return 3
    elif percentage >= 40:
        return 2
    else:
        return 1

@router.post("/start", response_model=GameSession)
async def start_game(settings: GameSettings):
    """Начинает новую математическую игру"""
    
    # Валидация настроек
    if settings.min_number >= settings.max_number:
        raise HTTPException(status_code=400, detail="Минимальное число должно быть меньше максимального")
    
    # Генерируем примеры
    examples = []
    for _ in range(settings.examples_count):
        operation = random.choice(settings.operations)
        example = generate_math_example(operation, settings.min_number, settings.max_number)
        examples.append(example)
    
    # Создаем игровую сессию
    session_id = f"game_{int(time.time())}_{random.randint(1000, 9999)}"
    session = GameSession(
        session_id=session_id,
        examples=examples,
        settings=settings,
        start_time=time.time()
    )
    
    active_sessions[session_id] = session
    
    return session

@router.get("/session/{session_id}", response_model=GameSession)
async def get_session(session_id: str):
    """Получает информацию об игровой сессии"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Игровая сессия не найдена")
    
    return active_sessions[session_id]

class AnswerRequest(BaseModel):
    answer: int

@router.post("/answer/{session_id}")
async def submit_answer(session_id: str, answer_data: AnswerRequest):
    """Отправляет ответ на текущий пример"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Игровая сессия не найдена")
    
    session = active_sessions[session_id]
    
    if session.current_example >= len(session.examples):
        raise HTTPException(status_code=400, detail="Игра уже завершена")
    
    current_example = session.examples[session.current_example]
    
    # Проверяем ответ
    if answer_data.answer == current_example.correct_answer:
        session.correct_answers += 1
    
    # Переходим к следующему примеру
    session.current_example += 1
    
    # Если игра завершена
    if session.current_example >= len(session.examples):
        session.end_time = time.time()
    
    return {
        "correct": answer_data.answer == current_example.correct_answer,
        "correct_answer": current_example.correct_answer,
        "game_completed": session.current_example >= len(session.examples)
    }

@router.post("/skip/{session_id}")
async def skip_example(session_id: str):
    """Пропускает текущий пример"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Игровая сессия не найдена")
    
    session = active_sessions[session_id]
    
    if session.current_example >= len(session.examples):
        raise HTTPException(status_code=400, detail="Игра уже завершена")
    
    # Переходим к следующему примеру
    session.current_example += 1
    
    # Если игра завершена
    if session.current_example >= len(session.examples):
        session.end_time = time.time()
    
    return {"game_completed": session.current_example >= len(session.examples)}

@router.get("/result/{session_id}", response_model=GameResult)
async def get_game_result(session_id: str):
    """Получает результат завершенной игры"""
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Игровая сессия не найдена")
    
    session = active_sessions[session_id]
    
    if session.end_time is None:
        raise HTTPException(status_code=400, detail="Игра еще не завершена")
    
    time_spent = session.end_time - session.start_time
    score = calculate_score(session.correct_answers, len(session.examples))
    percentage = (session.correct_answers / len(session.examples)) * 100
    
    result = GameResult(
        session_id=session_id,
        total_examples=len(session.examples),
        correct_answers=session.correct_answers,
        score=score,
        time_spent=time_spent,
        percentage=percentage
    )
    
    return result

@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Удаляет игровую сессию"""
    if session_id in active_sessions:
        del active_sessions[session_id]
    
    return {"message": "Сессия удалена"}
