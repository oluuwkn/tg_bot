import math
import hashlib
from datetime import datetime, date

ZODIAC_INFO = [
    ("Овна ♈️", "огненная"),
    ("Тельца ♉️", "земляная"),
    ("Близнецов ♊️", "воздушная"),
    ("Рака ♋️", "водная"),
    ("Льва ♌️", "огненная"),
    ("Девы ♍️", "земляная"),
    ("Весов ♎️", "воздушная"),
    ("Скорпиона ♏️", "водная"),
    ("Стрельца ♐️", "огненная"),
    ("Козерога ♑️", "земляная"),
    ("Водолея ♒️", "воздушная"),
    ("Рыб ♓️", "водная")
]

COLORS = [
    "Алый 🔴", "Изумрудный 🟢", "Глубокий синий 🔵", "Солнечно-желтый 🟡", 
    "Белоснежный ⚪️", "Фиолетовый 🟣", "Кремовый/Бежевый 🍦", "Шоколадный 🍫", 
    "Мятный 🌿", "Графитовый 🖤", "Золотистый 🪙", "Серебристый 🩶"
]

def get_moon_astronomy_data(target_date: date) -> tuple[int, tuple]:
    """
    Вычисляет эклиптические координаты Луны и Солнца (алгоритм Миуса).
    Возвращает (lunar_day, moon_zodiac_tuple).
    """
    year, month, day = target_date.year, target_date.month, target_date.day
    if month <= 2:
        year -= 1
        month += 12
    
    A = math.floor(year / 100)
    B = 2 - A + math.floor(A / 4)
    JD = math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + B - 1524.5
    
    T = (JD - 2451545.0) / 36525.0

    L_sun = (280.46646 + 36000.76983 * T) % 360
    M_sun = (357.52911 + 35999.05029 * T) % 360
    M_sun_rad = math.radians(M_sun)
    
    C_sun = (1.914602 - 0.004817 * T) * math.sin(M_sun_rad) + (0.019993 - 0.000101 * T) * math.sin(2 * M_sun_rad)
    lambda_sun = (L_sun + C_sun) % 360

    L_moon = (218.3164477 + 481267.88123421 * T) % 360
    M_moon = (134.9633964 + 477198.8675055 * T) % 360
    D_moon = (297.8501921 + 445267.1114034 * T) % 360
    F_moon = (93.2720950 + 483202.0175233 * T) % 360

    m_m = math.radians(M_moon)
    d_m = math.radians(D_moon)
    f_m = math.radians(F_moon)

    moon_perturb = (
        6.2886 * math.sin(m_m)
        + 1.2740 * math.sin(2 * d_m - m_m)
        + 0.6583 * math.sin(2 * d_m)
        + 0.2136 * math.sin(2 * m_m)
        - 0.1851 * math.sin(M_sun_rad)
        - 0.1143 * math.sin(2 * f_m)
    )

    lambda_moon = (L_moon + moon_perturb) % 360

    zodiac_index = math.floor(lambda_moon / 30) % 12
    moon_zodiac = ZODIAC_INFO[zodiac_index]

    elongation = (lambda_moon - lambda_sun) % 360
    lunar_day = math.floor(elongation / 12) + 1
    lunar_day = min(max(lunar_day, 1), 30)

    return lunar_day, moon_zodiac

def get_moon_horoscope(user_zodiac: str, raw_moon_phase: str = "") -> str:
    """
    Формирует лаконичный и точный лунный разбор:
    - Луна в знаке + фаза
    - Атмосфера дня
    - Уникальный прогноз под знак зодиака
    - Цвет дня
    """
    today = datetime.now().date()
    lunar_day, moon_zodiac = get_moon_astronomy_data(today)

    seed_str = f"{today.isoformat()}_{user_zodiac}_{lunar_day}"
    seed_val = int(hashlib.md5(seed_str.encode()).hexdigest(), 16)

    lucky_color = COLORS[(seed_val + 2) % len(COLORS)]
    clean_zodiac = user_zodiac.strip().title()

    if lunar_day in [1, 2, 3, 28, 29, 30]:
        atmosphere = "Мягкая, спокойная и накопительная. Благоприятное время для восстановления сил, замедления и тихих планов."
        forecasts = [
            f"Сегодня лунные энергии призывают не спешить. Для знака {clean_zodiac} это отличный шанс перевести дыхание и навести порядок в мыслях.",
            f"День благоприятствует спокойной и размеренной работе. {clean_zodiac} сможет легко увидеть главные приоритеты, если отсеет лишний шум.",
            f"Мягкий ритм дня позволит {clean_zodiac} сфокусироваться на себе. Доверяйте чувству комфорта и избегайте суеты."
        ]
    elif lunar_day in [8, 9, 15, 19, 23, 29]:
        atmosphere = "Интенсивная и динамичная. Эмоциональный фон восприимчив, но даёт хорошую концентрацию на задачах."
        forecasts = [
            f"Сегодня важно сохранять хладнокровие. Знаку {clean_zodiac} лучше направить эмоциональную энергию в полезные дела или физическую активность.",
            f"День проверки на выдержку. {clean_zodiac} легко решит сложный вопрос, если откажется от споров и сфокусируется на сути.",
            f"Энергетика дня подталкивает к обновлению. {clean_zodiac} почувствует прилив сил, если избавится от отвлекающих факторов."
        ]
    elif lunar_day in [10, 11, 12, 13, 14, 16, 17, 18]:
        atmosphere = "Высокая, насыщенная и продуктивная. Мозг работает четко, а жизненная энергия бьет ключом."
        forecasts = [
            f"Отличный момент для активных шагов! {clean_zodiac} сегодня на волне вдохновения — используйте момент для важных задач.",
            f"Энергия Луны открывает перед {clean_zodiac} хорошие перспективы. Ваша уверенность и инициатива дадут отличные плоды.",
            f"Благоприятные сутки для решительных действий. {clean_zodiac} сможет легко продвинуть давние идеи вперед."
        ]
    else:
        atmosphere = "Умеренная, размеренная и гармоничная. Подходит для системного движения вперед и утренних настроек."
        forecasts = [
            f"Стабильный день для последовательных дел. {clean_zodiac} добьется наилучших результатов через взвешенный и спокойный подход.",
            f"Гармоничное время для общения и текущих задач. {clean_zodiac} сможет легко найти баланс и взаимопонимание.",
            f"День не требует перегрузок, но дарует уверенный прогресс. {clean_zodiac} стоит придерживаться своего естественного ритма."
        ]

    forecast = forecasts[seed_val % len(forecasts)]
    phase_str = f", {raw_moon_phase}" if raw_moon_phase else ""

    text = (
        f"🌙 **Луна в знаке {moon_zodiac[0]}{phase_str}**\n\n"
        f"🌌 **Атмосфера дня:**\n{atmosphere}\n\n"
        f"🔮 **Прогноз для знака {clean_zodiac}:**\n{forecast}\n\n"
        f"🎨 **Цвет дня:** {lucky_color}"
    )

    return text

def get_month_name(month_num: int) -> str:
    months = ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", "августа", "сентября", "октября", "ноября", "декабря"]
    return months[month_num - 1]
