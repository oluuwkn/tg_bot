import asyncio
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiohttp import web

import config
import database
from weather import get_weather
from astro import get_moon_horoscope, get_month_name

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone="Asia/Almaty")

class Reg(StatesGroup):
    name = State()
    city = State()
    zodiac = State()

zodiac_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Овен ♈️", callback_data="Овен"), InlineKeyboardButton(text="Телец ♉️", callback_data="Телец")],
    [InlineKeyboardButton(text="Близнецы ♊️", callback_data="Близнецы"), InlineKeyboardButton(text="Рак ♋️", callback_data="Рак")],
    [InlineKeyboardButton(text="Лев ♌️", callback_data="Лев"), InlineKeyboardButton(text="Дева ♍️", callback_data="Дева")],
    [InlineKeyboardButton(text="Весы ♎️", callback_data="Весы"), InlineKeyboardButton(text="Скорпион ♏️", callback_data="Скорпион")],
    [InlineKeyboardButton(text="Стрелец ♐️", callback_data="Стрелец"), InlineKeyboardButton(text="Козерог ♑️", callback_data="Козерог")],
    [InlineKeyboardButton(text="Водолей ♒️", callback_data="Водолей"), InlineKeyboardButton(text="Рыбы ♓️", callback_data="Рыбы")]
])

main_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Получить дайджест сейчас")]],
    resize_keyboard=True
)

async def notify_admin(user_id: int, user_name: str, text: str):
    """Вспомогательная функция для пересылки сообщений и уведомлений в указанную группу."""
    if config.ADMIN_ID and config.ADMIN_ID != -1001234567890:
        try:
            admin_msg = f"📩 *Новое сообщение от пользователя!*\n👤 Имя: {user_name}\n🆔 ID: `{user_id}`\n💬 Текст: {text}"
            await bot.send_message(config.ADMIN_ID, admin_msg, parse_mode="Markdown")
        except Exception as e:
            print(f"Не удалось отправить уведомление в группу: {e}")

@dp.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    await database.log_message(message.from_user.id, message.from_user.full_name or "Неизвестно", message.text)
    await notify_admin(message.from_user.id, message.from_user.full_name or "Неизвестно", message.text)
    
    await message.answer("Привет! Как мне к тебе обращаться?")
    await state.set_state(Reg.name)

@dp.message(Reg.name)
async def name_handler(message: types.Message, state: FSMContext):
    await database.log_message(message.from_user.id, message.from_user.full_name or "Неизвестно", message.text)
    await notify_admin(message.from_user.id, message.from_user.full_name or "Неизвестно", message.text)
    
    await state.update_data(name=message.text)
    await message.answer(f"Супер, {message.text}! В каком городе ты находишься? (Например: Алматы)")
    await state.set_state(Reg.city)

@dp.message(Reg.city)
async def city_handler(message: types.Message, state: FSMContext):
    await database.log_message(message.from_user.id, message.from_user.full_name or "Неизвестно", message.text)
    await notify_admin(message.from_user.id, message.from_user.full_name or "Неизвестно", message.text)
    
    await state.update_data(city=message.text)
    await message.answer("Отлично! Последний шаг: выбери свой знак зодиака", reply_markup=zodiac_kb)
    await state.set_state(Reg.zodiac)

@dp.callback_query(Reg.zodiac)
async def zodiac_handler(callback: types.CallbackQuery, state: FSMContext):
    zodiac = callback.data
    data = await state.get_data()
    
    await database.add_user(callback.from_user.id, data['name'], data['city'], zodiac)
    await database.log_message(callback.from_user.id, data['name'], f"Выбрал знак: {zodiac}")
    await notify_admin(callback.from_user.id, data['name'], f"Завершил регистрацию! Город: {data['city']}, Знак: {zodiac}")
    
    await callback.message.edit_text(
        f"🎉 Всё готово, *{data['name']}*!\n"
        f"📍 Твой город: {data['city']}\n"
        f"🔮 Знак: {zodiac}\n\n"
        f"Каждое утро я буду присылать тебе дайджест. Но ты можешь запросить его в любой момент через меню ниже!",
        parse_mode="Markdown"
    )
    await callback.message.answer("Меню активировано 👇", reply_markup=main_kb)
    await state.clear()

async def generate_digest(user_id: int):
    """Генерация персонализированного дайджеста с датой, погодой, лунным разбором, цитатой и комплиментом."""
    user = await database.get_user(user_id)
    if not user:
        return "Произошла ошибка. Пожалуйста, пройдите регистрацию заново: /start"
    
    weather = await get_weather(user['city'])
    if isinstance(weather, str):
        return weather
    
    today = datetime.now()
    date_str = f"{today.day} {get_month_name(today.month)} {today.year} г."

    astro_digest = get_moon_horoscope(user['zodiac'], raw_moon_phase=weather['moon'])
    
    quote = database.get_daily_quote(user_id)
    compliment = database.get_daily_compliment(user_id)

    uv_warning = ""
    try:
        if float(weather['uv']) >= 5:
            uv_warning = "\n🧴 *Защита от солнца:* УФ-индекс высокий, обязательно нанесите SPF перед выходом!"
    except (ValueError, TypeError):
        pass

    message = (
        f"☀️ *Доброе утро, {user['name']}! Твой дайджест:*\n\n"
        f"🗓 *{date_str}*\n\n"
        f"📍 *Погода в г. {weather['city_name']}:* {weather['condition']}\n"
        f"🌡 Температура: {weather['temp']} (Ощущается как {weather['feels_like']})\n"
        f"💧 Влажность: {weather['humidity']} | 💨 Ветер: {weather['wind']}\n"
        f"☀️ УФ-индекс: {weather['uv']}{uv_warning}\n\n"
        f"🔮 *ЛУННЫЙ РАЗБОР НА СЕГОДНЯ:*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{astro_digest}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💬 *Цитата дня:*\n_{quote}_\n\n"
        f"✨ *Специально для тебя:*\n_{compliment}_"
    )
    return message

@dp.message(F.text == "Получить дайджест сейчас")
async def send_digest_now(message: types.Message):
    await database.log_message(message.from_user.id, message.from_user.full_name or "Неизвестно", message.text)
    await notify_admin(message.from_user.id, message.from_user.full_name or "Неизвестно", message.text)
    
    loading_msg = await message.answer("🔍 Собираю прогноз погоды и положение Луны...")
    text = await generate_digest(message.from_user.id)
    await loading_msg.delete()
    await message.answer(text, parse_nomarkdown=True, parse_mode="Markdown")

@dp.message()
async def log_all_messages(message: types.Message):
    """Логирует любое другое текстовое сообщение от пользователя и пересылает в группу."""
    if message.text:
        await database.log_message(
            message.from_user.id, 
            message.from_user.full_name or "Неизвестно", 
            message.text
        )
        await notify_admin(message.from_user.id, message.from_user.full_name or "Неизвестно", message.text)

async def scheduled_mailing():
    users = await database.get_all_users()
    for user in users:
        try:
            text = await generate_digest(user['user_id'])
            await bot.send_message(user['user_id'], text, parse_mode="Markdown")
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Не удалось отправить пользователю {user['user_id']}: {e}")

async def handle_ping(request):
    """Веб-страница для проверки статуса Render (Health Check)."""
    return web.Response(text="Bot is running 24/7!")

async def main():
    await database.init_db()
    scheduler.add_job(scheduled_mailing, 'cron', hour=config.DIGEST_HOUR, minute=config.DIGEST_MINUTE)
    scheduler.start()

    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    print(f"Бот успешно запущен! Веб-сервер слушает порт {port}")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
