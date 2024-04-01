import logging

from aiogram import Router, types, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command


from ..db import add_user, get_user_info
from ..config_reader import config
from ..api_client import get_service_list
from .. import text, keyboards
from ..keyboards import create_service_list_keyboard, Pagination


router = Router()


@router.message(Command("start"))
async def start_handler(message: Message):
    """
    Handle the /start command.
    """
    print("Handler start_handler called")  # Добавляем отладочное сообщение
    username = message.from_user.username
    telegram_id = message.from_user.id
    add_user(username, telegram_id)
    await message.answer(text.greet.format(name=message.from_user.full_name),
                         reply_markup=keyboards.create_main_menu_keyboard())


@router.message(F.text == "👤 Мой профиль")
async def profile_button_handler(message: Message):
    """
    Handle profile button press.
    """
    print("Handler profile_button_handler called")  # Добавляем отладочное сообщение
    if message.text == "👤 Мой профиль":
        user_id = message.from_user.id
        user_info = get_user_info(user_id)

        if user_info:
            await message.answer(format_user_info(user_info))
        else:
            await message.answer("Информация о вашем профиле не найдена.")


def format_user_info(user_info):
    """
    Format user information.
    """
    return f"Информация о вашем профиле:\n" \
           f"👤 Username: {user_info[2]}\n" \
           f"🤖 Telegram ID: {user_info[1]}\n" \
           f"💼 Сделано заказов: {user_info[3]}\n" \
           f"💰 Баланс кошелька: {user_info[4]}\n" \
           f"🤝 Количество рефералов: {user_info[5]}"


# Глобальная переменная для хранения списка клавиатур
network_keyboards = {}


@router.message(F.text == "💼 Перечень услуг накрутки")
async def service_list_handler(message: types.Message):
    """
    Handle the service list button press.
    """
    print("Handler service_list_handler called")

    try:
        if message.text == "💼 Перечень услуг накрутки":
            # Получение списка услуг и создание клавиатуры для перечня услуг
            api_key = config.api_key.get_secret_value()
            service_list_data = await get_service_list(api_key)

            # Проверка на наличие списка услуг
            if service_list_data:
                keyboard_list = create_service_list_keyboard(service_list_data)

                # Отправляем первую клавиатуру из списка
                if keyboard_list:
                    # Сохраняем остальные клавиатуры в пользовательских данных
                    network_keyboards[message.chat.id] = keyboard_list[:]

                    # Отправляем первую клавиатуру
                    await message.answer("Выберите сервис для накрутки:", reply_markup=keyboard_list[0].as_markup())
                    print("First keyboard sent successfully")
                else:
                    await message.answer("Ошибка при создании клавиатуры.")
                    print("Failed to create keyboard")
            else:
                await message.answer("Ошибка при получении списка услуг.")
                print("Failed to get service list")

    except Exception as e:
        logging.error(f"Error in handling service list request: {e}")


# Глобальная переменная для хранения текущей страницы для каждого пользователя
current_page_dict = {}


@router.callback_query(Pagination.filter(F.action.in_(["prev", "next"])))
async def pagination_handler(callback_query: CallbackQuery, callback_data: Pagination):
    user_id = callback_query.from_user.id
    print(f"Pagination handler called by user ID: {user_id}")

    if user_id in network_keyboards:
        keyboard_list = network_keyboards[user_id]
        if keyboard_list:
            # Получаем текущую страницу пользователя или устанавливаем 0, если пользователь новый
            current_page = current_page_dict.get(user_id, 0)

            if callback_data.action == "prev":
                current_page -= 1
            elif callback_data.action == "next":
                current_page += 1

            # Проверяем на выход за границы списка клавиатур
            if current_page < 0:
                # Отправляем сообщение о том, что пользователь уже на первой странице
                print("User is already on the first page")
                await callback_query.answer("You are already on the first page", show_alert=True)
                current_page = 0
            elif current_page >= len(keyboard_list):
                # Отправляем сообщение о том, что пользователь уже на последней странице
                print("User is already on the last page")
                await callback_query.answer("You are already on the last page", show_alert=True)
                current_page = len(keyboard_list) - 1

            # Сохраняем текущую страницу пользователя
            current_page_dict[user_id] = current_page

            print(f"Pagination: Action - {callback_data.action}, Current Page - {current_page}")

            # Удаляем предыдущую клавиатуру
            await callback_query.message.delete_reply_markup()

            # Отправляем новую клавиатуру
            await callback_query.message.edit_reply_markup(reply_markup=keyboard_list[current_page].as_markup())
        else:
            await callback_query.answer("Please send the service list first")
    else:
        await callback_query.answer("Please send the service list first")