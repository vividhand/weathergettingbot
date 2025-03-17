import aiogram
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import CallbackQuery
from config import API, token
import requests
from urllib3.filepost import choose_boundary

bot = Bot(token=token)
dp = Dispatcher()
API = API
user_languages = {}


inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Русский", callback_data="Russian")],
        [InlineKeyboardButton(text="English", callback_data="English")]
    ]
)
choose_sticker_weather = ""
choose_sticker_temperature = "🌋"
stikers = {"sunny": "☀️", "cloud": "☁️", "rain": "🌧️", "tunder": "⛈️", "snow": "❄️", "clear": "⛅", "cold": "❄️", "very_cold": "🔵",
           "hot": "🔥", "very_hot": "🌋", "warm": "🌡️", "cool": "🌤️"}
@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Hello, I am bot for geting weather your city...\n"
                         "Привет, Я бот спомощью которого ты можешь узнать погоду своего города...\n"
                         "Use command /weather for getting weathers...\n"
                         "Используй команду /weather чтоб узнать погоду...")
@dp.message(Command("language"))
async def language(message: Message):
    await message.answer("Choose language / Выберите язык:", reply_markup=inline_keyboard)
@dp.callback_query(lambda c: c.data in ["Russian", "English"])
async def set_language(callback: CallbackQuery):
    user_languages[callback.from_user.id] = callback.data
    lang_text = "Язык изменён на Русский" if callback.data == "Russian" else "Language changed to English"
    await callback.message.answer(lang_text)

@dp.message(Command("weather"))
async def weather(message: Message):
    user_id = message.from_user.id
    language = user_languages.get(user_id, "English")
    if language == "English":
        await message.answer("Send city name...")
    else:
        await message.answer("Введите название города...")

    @dp.message()
    async def get_city_name(message: Message):
        if message.text.strip().lower() != "/weather" or message.text.strip().lower() != "/language" or message.text.strip().lower() != "/start":
            city = message.text.strip().lower()
        weather = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric")
        data = weather.json()

        if data["cod"] == 200:
            weather_main = data["weather"][0]["main"]
            temperature_main = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            temperature_minimal = data["main"]["temp_min"]
            temperature_max = data["main"]["temp_max"]
            wind_speed = data["wind"]["speed"]

            global choose_sticker_weather, choose_sticker_temperature

            if weather_main == "Clouds":
                choose_sticker_weather = stikers["cloud"]
            elif weather_main == "Clear":
                choose_sticker_weather = stikers["clear"]
            elif weather_main == "Sun":
                choose_sticker_weather = stikers["sunny"]
            elif weather_main == "Rain":
                choose_sticker_weather = stikers["rain"]
            elif weather_main == "Snow":
                choose_sticker_weather = stikers["snow"]


            if temperature_main < -10.00:
                choose_sticker_temperature = stikers["very_cold"]
            elif temperature_main < 0.00 and temperature_main >= -10.00:
                choose_sticker_temperature = stikers["cold"]
            elif temperature_main >= 0.00 and temperature_main <= 15.00:
                choose_sticker_temperature = stikers["cool"]
            elif temperature_main > 15.00 and temperature_main <= 25.00:
                choose_sticker_temperature = stikers["warm"]
            elif temperature_main > 25.00 and temperature_main <= 35.00:
                choose_sticker_temperature = stikers["hot"]
            elif temperature_main > 35.00:
                choose_sticker_temperature = stikers["very_cold"]

            if language == "English":
                await message.answer(f"<b>City: {city}\nWeather: {weather_main}{choose_sticker_weather}\nTemperature: {temperature_main}{choose_sticker_temperature}\n"
                                     f"Feels like: {feels_like}{choose_sticker_temperature}\n"
                                    f"Temperature minimum: {temperature_minimal}{choose_sticker_temperature}\nT"
                                     f"emperature max: {temperature_max}{choose_sticker_temperature}\n"
                                     f"Wind speed: {wind_speed}</b>", parse_mode = "HTML")
            else:
                await message.answer(f"<b>Город: {city}\nПогода: {weather_main}{choose_sticker_weather}\nТемпература: {temperature_main}{choose_sticker_temperature}"
                                     f"\nОщущается как: {feels_like}\n{choose_sticker_temperature}"
                                    f"Минимальная температура: {temperature_minimal}{choose_sticker_temperature}\nМаксимальная температура: {temperature_max}{choose_sticker_temperature}\n"
                                     f"Скорость ветра: {wind_speed}</b>", parse_mode = "HTML")
        else:
            await message.answer("City not found..." if language == "English" else "Город не найден...")
@dp.message(Command("help"))
async def help(message: Message):
    user_id = message.from_user.id
    language = user_languages.get(user_id, "English")
    if language == "English":
        await message.answer("/start - <b>Starting bot</b>\n"
                             "/weather - <b>Getting weather your city</b>\n"
                             "/help - <b>Send all commands\n</b>"
                             "/language - <b>Changed languages</b>", parse_mode = "HTML")
    else:
        await message.answer("/start - <b>Запустит бота</b>\n"
                             "/weather - <b>Выведет погоду указаного города</b>\n"
                             "/help - <b>Выведет все комманды используемые ботом\n</b>"
                             "/language - <b>Позволит сменить язык бота</b>", parse_mode="HTML")
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
