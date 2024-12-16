from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils import executor
import sqlite3
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage

main_buttons = ReplyKeyboardMarkup([
    [
        KeyboardButton("🌕 Coin'larim"), KeyboardButton('🛒 DevStep Shop')
    ],

    [
        KeyboardButton('🌐 Saytga o\'tish'), KeyboardButton('O\'chirish')
    ]
], resize_keyboard=True)

API_TOKEN = '7370433819:AAEGOPlCEVFwq7jG4EaHjeiSw5D2hlQwe5A'


bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

class Registration(StatesGroup):
    waiting_for_modme_id = State()
    waiting_for_password = State()

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    cursor.execute("SELECT telegram_bot_register, name FROM accounts_user WHERE telegram_bot_register = ?", (message.from_user.id,))
    result = cursor.fetchone()

    if result and result[0]:
        await message.answer(f"Salom, {result[1]}! Xush kelibsiz!", reply_markup=main_buttons)
    else:
        await message.answer("Salom! DevStep ning rasmiy botiga xush kelibsiz!\nProfilga kirish uchun ro'yxatdan o'tishingiz kerak.")
        await message.answer("Modme IDingizni kiriting:")
        await Registration.waiting_for_modme_id.set()

@dp.message_handler(state=Registration.waiting_for_modme_id)
async def process_modme_id(message: types.Message, state: FSMContext):
    await state.update_data(modme_id=message.text)
    await message.answer("Parolingizni kiriting:")
    await Registration.waiting_for_password.set()

@dp.message_handler(state=Registration.waiting_for_password)
async def process_password(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    data = await state.get_data()
    modme_id = data['modme_id']
    password = message.text

    cursor.execute("SELECT name FROM accounts_user WHERE modme_id = ? AND password = ?", (modme_id, password))
    user = cursor.fetchone()

    if user:
        name = user[0]
        cursor.execute(f"UPDATE accounts_user SET telegram_bot_register = {chat_id} WHERE modme_id = ?", (modme_id,))
        conn.commit()

        await message.answer(f"Xush kelibsiz, {name}!", reply_markup=main_buttons)
        await state.finish()
    else:
        await message.answer("Modme ID yoki parol xato. Qaytadan urinib ko'ring:\nModme IDingizni kiriting:")
        await Registration.waiting_for_modme_id.set()







@dp.message_handler(text="🌕 Coin'larim")

async def coin_list(message: types.Message):
    cursor.execute("SELECT total_coins FROM accounts_user WHERE telegram_bot_register =?", (message.from_user.id,))
    coins = cursor.fetchone()[0]
    await message.answer(f"Sizda {coins}🌕 bor.", reply_markup=main_buttons)



@dp.message_handler(text="🛒 DevStep Shop")
async def devstep_shop(message: types.Message):
    await message.answer("DevStep Shop - https://devstep.pythonanywhere.com/shop/", reply_markup=main_buttons)



@dp.message_handler(text="🌐 Saytga o'tish")
async def go_site(message: types.Message):
    await message.answer("Sayt manzili - https://devstep.pythonanywhere.com", reply_markup=main_buttons)




@dp.message_handler(text="O'chirish")
async def delete_account(message: types.Message):
    # modme_id = cursor.execute("SELECT modme_id FROM accounts_user WHERE telegram_bot_register = ?", (message.chat.id, ))
    cursor.execute(f"UPDATE accounts_user SET telegram_bot_register = 0 WHERE telegram_bot_register = ?", (message.chat.id,))

    conn.commit()
    await message.answer("Sizning profilingiz o'chirildi.", reply_markup=ReplyKeyboardRemove())


async def start_bot():
    try:
        await dp.start_polling()
    except Exception as e:
        if "TerminatedByOtherGetUpdates" in str(e):
            print("TerminatedByOtherGetUpdates xatosi ignor qilindi.")
        else:
            raise