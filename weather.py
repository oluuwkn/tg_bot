import aiohttp
from config import WEATHER_API_KEY

MOON_PHASES = {
    "New Moon": "Новолуние 🌑",
    "Waxing Crescent": "Растущий месяц 🌒",
    "First Quarter": "Первая четверть 🌓",
    "Waxing Gibbous": "Растущая луна 🌔",
    "Full Moon": "Полнолуние 🌕",
    "Waning Gibbous": "Убывающая луна 🌖",
    "Last Quarter": "Третья четверть 🌗",
    "Waning Crescent": "Убывающий месяц 🌘"
}

async def get_weather(city: str) -> dict | str:
    """Делает запрос к WeatherAPI и форматирует название города."""
    url = "http://api.weatherapi.com/v1/forecast.json"
    
    cleaned_city = city.strip().lower()
    is_almaty = False
    
    # Жесткая привязка Алматы и его районов к точным координатам
    if any(alias in cleaned_city for alias in ["алматы", "almaty", "алма-ата", "alma-ata"]):
        query_city = "43.2389,76.8897"
        is_almaty = True
    else:
        query_city = city

    params = {
        "key": WEATHER_API_KEY,
        "q": query_city,
        "days": 1,
        "lang": "ru"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status != 200:
                return "Не удалось найти город. Проверьте правильность названия."
            
            data = await response.json()
            
            location = data['location']
            current = data['current']
            astro = data['forecast']['forecastday'][0]['astro']
            
            
            if is_almaty or location['name'].lower() in ["almaty"]:
                resolved_city = "Алматы, Казахстан"
            else:
                resolved_city = f"{location['name']}, {location['country']}"
            
            temp = current['temp_c']
            feels_like = current['feelslike_c']
            humidity = current['humidity']
            wind_kph = current['wind_kph']
            wind_ms = round(wind_kph * 1000 / 3600, 1) # Перевод км/ч в м/с
            uv = current['uv']
            condition = current['condition']['text']
            
            raw_moon = astro['moon_phase']
            moon = MOON_PHASES.get(raw_moon, raw_moon)
            
            return {
                "city_name": resolved_city,
                "temp": f"{temp}°C",
                "feels_like": f"{feels_like}°C",
                "humidity": f"{humidity}%",
                "wind": f"{wind_ms} м/с",
                "uv": uv,
                "condition": condition,
                "moon": moon
            }