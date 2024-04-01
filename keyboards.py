from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

import logging


# Определение клавиатур

# Клавиатура основного меню
def create_main_menu_keyboard():
    # Создаем кнопки для каждого пункта меню
    button_service_list = KeyboardButton(text="💼 Перечень услуг накрутки")
    button_support_chat = KeyboardButton(text="🧑‍💻 Чат с поддержкой")
    button_my_profile = KeyboardButton(text="👤 Мой профиль")
    button_my_orders = KeyboardButton(text="📑 Мои заказы")
    button_balance_recharge = KeyboardButton(text="💰 Пополнить баланс")

    # Создаем разметку клавиатуры
    menu_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [button_service_list, button_support_chat],
            [button_my_profile, button_my_orders],
            [button_balance_recharge]
        ],
        resize_keyboard=True
    )

    return menu_keyboard


# Клавиатура пагинации
class Pagination(CallbackData, prefix="pag"):
    action: str
    page: int


def paginator(page: int = 0):
    pagination_keyboard = InlineKeyboardBuilder()
    pagination_keyboard.add(
        InlineKeyboardButton(text="⬅ Previous", callback_data=Pagination(action="prev", page=page).pack()),
        InlineKeyboardButton(text="Next ➡", callback_data=Pagination(action="next", page=page).pack())
    )
    return pagination_keyboard


def create_service_list_keyboard(service_list_data):
    try:
        print("Начало создания клавиатуры")
        keyboard_list = []
        social_networks = set()

        # Получаем список социальных сетей из данных о сервисах
        for service_data in service_list_data:
            category = service_data.get('category')
            social_network = category.split('-')[0].strip().capitalize()

            # Исключаем добавление названий соцсетей с флагами стран
            if ord(social_network[0]) >= 127397:  # Проверяем, является ли первый символ символом флага страны
                social_network = social_network[2:].strip().capitalize()  # Удаляем символы флага страны

            social_networks.add(social_network)

        # Сортируем социальные сети по алфавиту
        sorted_networks = sorted(social_networks)

        max_buttons_per_chunk = 30  # Максимальное количество кнопок в каждом чанке
        chunks = [sorted_networks[i:i + max_buttons_per_chunk] for i in
                  range(0, len(sorted_networks), max_buttons_per_chunk)]

        print(f"Количество клавиатур: {len(chunks)}")

        for i, chunk in enumerate(chunks):
            keyboard_buttons = []
            for network in chunk:
                button = InlineKeyboardButton(text=network, callback_data=f"network_{network.lower()}")
                keyboard_buttons.append(button)

            keyboard_markup = InlineKeyboardBuilder()
            keyboard_markup.add(*keyboard_buttons)
            keyboard_markup.adjust(3)

            # Создаем кнопки пагинации
            pagination = paginator(page=i)  # Создаем пагинатор для текущей страницы

            # Добавляем кнопки пагинации к клавиатуре
            keyboard_markup.attach(pagination)

            # Теперь добавляем готовую клавиатуру в список
            keyboard_list.append(keyboard_markup)

        return keyboard_list
    except Exception as e:
        logging.error(f"Ошибка при создании клавиатуры: {e}")
        return None
