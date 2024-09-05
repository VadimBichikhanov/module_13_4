from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, StateFilter, CommandStart
import logging
import asyncio
from os import getenv

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Получение токена бота из переменных окружения
API_TOKEN = getenv('TELEGRAM_TOKEN')

# Проверка наличия токена
if not API_TOKEN:
    logging.error("TELEGRAM_TOKEN не найден в переменных окружения")
    exit(1)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Определение группы состояний
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

# Обработчик команды /start
@dp.message(CommandStart())
async def command_start_handler(message: Message):
    await message.answer('Привет! Я бот, который поможет тебе рассчитать норму калорий. \nИспользуй команду /calories, чтобы начать.')

# Обработчик для начала цепочки
@dp.message(Command("calories"))
async def set_age(message: Message, state: FSMContext):
    await message.reply('Введите свой возраст:')
    await state.set_state(UserState.age)

# Обработчик для ввода возраста
@dp.message(StateFilter(UserState.age))
async def set_growth(message: Message, state: FSMContext):
    await process_numeric_input(message, state, 'age', 'Введите свой рост:', UserState.growth)

# Обработчик для ввода роста
@dp.message(StateFilter(UserState.growth))
async def set_weight(message: Message, state: FSMContext):
    await process_numeric_input(message, state, 'growth', 'Введите свой вес:', UserState.weight)

# Обработчик для ввода веса и вычисления калорий
@dp.message(StateFilter(UserState.weight))
async def send_calories(message: Message, state: FSMContext):
    await process_numeric_input(message, state, 'weight', 'Ваша норма калорий:', UserState.weight, calculate_calories)

async def process_numeric_input(message: Message, state: FSMContext, key: str, prompt: str, next_state: State, callback=None):
    try:
        value = int(message.text)
        await state.update_data(**{key: value})
        if callback:
            await callback(message, state)
        else:
            await message.reply(prompt)
            await state.set_state(next_state)
    except ValueError:
        await message.reply('Пожалуйста, введите корректное число.')

async def calculate_calories(message: Message, state: FSMContext):
    data = await state.get_data()
    age = data['age']
    growth = data['growth']
    weight = data['weight']

    # Формула Миффлина - Сан Жеора для женщин
    calories = 10 * weight + 6.25 * growth - 5 * age - 161

    await message.reply(f'Ваша норма калорий: {calories:.2f} ккал в день.')
    await state.clear()

# Функция для перехвата сообщений
@dp.message()
async def handle_message(message: Message):
    await message.answer('Привет! Я бот, который поможет тебе рассчитать норму калорий. \nИспользуй команду /calories, чтобы начать.')

async def main() -> None:
    # Запуск обработки событий
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())