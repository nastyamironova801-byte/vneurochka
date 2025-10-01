from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
import asyncio

API_TOKEN = "7986794519:AAHEb6PZesNe4e3bMWvbcSjBgDFARoEKnqs"

children_list = [
    "Бадор Алиса", "Бадор Василиса", "Бортников Артём", "Брюзгин Виталий",
    "Виноградов Дмитрий", "Гончаров Максим", "Губанов Игорь", "Дамжиков Даян",
    "Дралова Виктория", "Ефимов Михаил", "Жуков Роман", "Завьялова Александра",
    "Игнатов Владимир", "Иркабаев Мирон", "Кольцов Егор", "Коношенок Иван",
    "Крашенинников Лев", "Крючкова Анна", "Матвеева София", "Михайлова Ульяна",
    "Пайо Ева", "Породнов Георгий", "Разнатовская Анна", "Розанова Анастасия",
    "Скребнева Юлия", "Суслова Алиса", "Титова Мария", "Устюгова Ариана",
    "Чернопятов Иван", "Черченко Глеб", "Экслер Даниил", "Яковлева Таисия"
]

days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

data_store = {day: {} for day in days_of_week}

# ----------------- FSM -----------------
class ChildForm(StatesGroup):
    choose_child = State()
    choose_day = State()
    extracurricular = State()
    dot1 = State()
    dot2 = State()
    pickup_time = State()
    note = State()

# ----------------- Клавиатуры -----------------
def main_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Выбрать ребенка")],
            [KeyboardButton(text="Посмотреть общий итог")]
        ],
        resize_keyboard=True
    )

def children_kb():
    buttons = [[KeyboardButton(text=child)] for child in children_list]
    buttons.append([KeyboardButton(text="Назад")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def days_kb():
    buttons = [[KeyboardButton(text=day)] for day in days_of_week]
    buttons.append([KeyboardButton(text="Назад")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def back_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Назад")]],
        resize_keyboard=True
    )

# ----------------- Команды -----------------
@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu_kb())

# ----------------- Логика -----------------
@dp.message(F.text == "Выбрать ребенка")
async def choose_child_start(message: Message, state: FSMContext):
    await state.set_state(ChildForm.choose_child)
    await message.answer("Выберите ребенка:", reply_markup=children_kb())

@dp.message(F.text == "Посмотреть общий итог")
async def show_summary(message: Message):
    text = ""
    for day in days_of_week:
        text += f"=== {day} ===\n"
        children = data_store[day]
        if not children:
            text += "Нет данных\n"
        else:
            # сортируем по алфавиту
            for child in sorted(children):
                info = children[child]
                text += (
                    f"{child}: Внеурочка={info['extracurricular']}, "
                    f"ДОТ-1={info['dot1']}, ДОТ-2={info['dot2']}, "
                    f"Время ухода={info['pickup']}, Примечание={info['note']}\n"
                )
        text += "\n"
    await message.answer(text)

@dp.message(F.text == "Главное меню")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Главное меню:", reply_markup=main_menu_kb())

# ----------------- FSM -----------------
@dp.message(ChildForm.choose_child, F.text.in_(children_list))
async def child_chosen(message: Message, state: FSMContext):
    await state.update_data(child=message.text)
    await state.set_state(ChildForm.choose_day)
    await message.answer("Выберите день недели:", reply_markup=days_kb())

@dp.message(ChildForm.choose_child, F.text == "Назад")
async def back_to_main_from_child(message: Message, state: FSMContext):
    await state.clear()
    await start(message, state)

@dp.message(ChildForm.choose_day, F.text.in_(days_of_week))
async def day_chosen(message: Message, state: FSMContext):
    await state.update_data(day=message.text)
    await state.set_state(ChildForm.extracurricular)
    await message.answer("Введите внеурочную деятельность:", reply_markup=back_kb())

@dp.message(ChildForm.choose_day, F.text == "Назад")
async def back_to_child(message: Message, state: FSMContext):
    await state.set_state(ChildForm.choose_child)
    await message.answer("Выберите ребенка:", reply_markup=children_kb())

@dp.message(ChildForm.extracurricular)
async def extracurricular_input(message: Message, state: FSMContext):
    await state.update_data(extracurricular=message.text)
    await state.set_state(ChildForm.dot1)
    await message.answer("Введите ДОТ-1:", reply_markup=back_kb())

@dp.message(ChildForm.extracurricular, F.text == "Назад")
async def back_to_day_from_extracurricular(message: Message, state: FSMContext):
    await state.set_state(ChildForm.choose_day)
    await message.answer("Выберите день недели:", reply_markup=days_kb())

@dp.message(ChildForm.dot1)
async def dot1_input(message: Message, state: FSMContext):
    await state.update_data(dot1=message.text)
    await state.set_state(ChildForm.dot2)
    await message.answer("Введите ДОТ-2:", reply_markup=back_kb())

@dp.message(ChildForm.dot1, F.text == "Назад")
async def back_to_extracurricular(message: Message, state: FSMContext):
    await state.set_state(ChildForm.extracurricular)
    await message.answer("Введите внеурочную деятельность:", reply_markup=back_kb())

@dp.message(ChildForm.dot2)
async def dot2_input(message: Message, state: FSMContext):
    await state.update_data(dot2=message.text)
    await state.set_state(ChildForm.pickup_time)
    await message.answer("Введите время ухода из школы:", reply_markup=back_kb())

@dp.message(ChildForm.dot2, F.text == "Назад")
async def back_to_dot1(message: Message, state: FSMContext):
    await state.set_state(ChildForm.dot1)
    await message.answer("Введите ДОТ-1:", reply_markup=back_kb())

@dp.message(ChildForm.pickup_time)
async def pickup_input(message: Message, state: FSMContext):
    await state.update_data(pickup=message.text)
    await state.set_state(ChildForm.note)
    await message.answer("Введите примечание (по желанию):", reply_markup=back_kb())

@dp.message(ChildForm.pickup_time, F.text == "Назад")
async def back_to_dot2(message: Message, state: FSMContext):
    await state.set_state(ChildForm.dot2)
    await message.answer("Введите ДОТ-2:", reply_markup=back_kb())

@dp.message(ChildForm.note)
async def note_input(message: Message, state: FSMContext):
    await state.update_data(note=message.text)
    data = await state.get_data()
    day = data["day"]
    child = data["child"]

    # сохраняем данные
    data_store.setdefault(day, {})
    data_store[day][child] = {
        "extracurricular": data["extracurricular"],
        "dot1": data["dot1"],
        "dot2": data["dot2"],
        "pickup": data["pickup"],
        "note": data["note"]
    }

    # формируем итог по ребенку на этот день
    info = data_store[day][child]
    child_summary = (
        f"✅ Ребенок {child} записан на {day}:\n"
        f"Внеурочная деятельность: {info['extracurricular']}\n"
        f"ДОТ-1: {info['dot1']}\n"
        f"ДОТ-2: {info['dot2']}\n"
        f"Время ухода: {info['pickup']}\n"
        f"Примечание: {info['note']}"
    )

    await state.clear()
    await message.answer(child_summary, reply_markup=main_menu_kb())

@dp.message(ChildForm.note, F.text == "Назад")
async def back_to_pickup(message: Message, state: FSMContext):
    await state.set_state(ChildForm.pickup_time)
    await message.answer("Введите время ухода из школы:", reply_markup=back_kb())

# ----------------- Запуск -----------------
if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
