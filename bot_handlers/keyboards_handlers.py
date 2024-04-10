import logging

from aiogram import Router, types, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..db import add_user, get_user_info
from ..config_reader import config
from ..api_client import get_service_list
from .. import text, keyboards
from ..keyboards import Pagination, create_service_list_keyboard, \
    create_social_network_keyboards, create_third_level_keyboards, \
    create_fourth_level_keyboard

keyboard_router = Router()


# Определение обработчиков
# Обработчик команды /start
@keyboard_router.message(Command("start"))
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


# Обработчик ЛК
@keyboard_router.message(F.text == "👤 Мой профиль")
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


# Форматирование вывода данных ЛК
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


@keyboard_router.message(F.text == "🧑‍💻 Чат с поддержкой")
async def support_chat(message: Message):
    """
    Chat support button press.
    """
    if message.text == "🧑‍💻 Чат с поддержкой":
        # Удаляем предыдущую inline клавиатуру
        await message.delete_reply_markup()

        # Отправляем пользователю ссылку на телеграм чат в виде сообщения
        await message.answer("Вы можете связаться с нами в нашем чате поддержки: "
                             "[BestSmmLike Support](https://t.me/bestsmmlike)")


# # Обработчик списка услуг -> вывод клавиатур 1 уровня
# !!! TO_DO - пересмотреть логику для устранения использования global variables !!!
# Глобальная переменная для хранения списка клавиатур
network_keyboards = {}


@keyboard_router.message(F.text == "💼 Перечень услуг накрутки")
async def service_list_handler(message: types.Message, state: FSMContext):
    """
    Handle the service list button press.
    """
    print("Handler service_list_handler called")

    try:
        if message.text == "💼 Перечень услуг накрутки":
            # Получение списка услуг и создание клавиатуры для перечня услуг
            api_key = config.api_key.get_secret_value()
            service_list_data = await get_service_list(api_key)
            # Запись service_list_data в state_data
            await state.update_data(service_list_data=service_list_data)

            # Проверка на наличие списка услуг
            if service_list_data:
                keyboard_list = create_service_list_keyboard(service_list_data)

                # Отправляем первую клавиатуру из списка
                if keyboard_list:
                    # Сохраняем остальные клавиатуры в пользовательских данных
                    network_keyboards[message.chat.id] = keyboard_list[:]

                    # Отправляем первую клавиатуру
                    await message.answer("Выберите сервис для накрутки:", reply_markup=keyboard_list[0].as_markup())
                    # print("First keyboard sent successfully")
                else:
                    await message.answer("Ошибка при создании клавиатуры.")
                    print("Failed to create keyboard")
            else:
                await message.answer("Ошибка при получении списка услуг.")
                print("Failed to get service list")

    except Exception as e:
        logging.error(f"Error in handling service list request: {e}")
        print(f"Error in handling service list request: {e}")


# Обработчики коллбэков
# Глобальная переменная для хранения предыдущей клавиатуры для каждого пользователя
previous_keyboard_dict = {}
# Глобальная переменная для хранения текущей страницы для каждого пользователя
current_page_dict = {}


# Обработчик кнопок пагинации на клавиатурах 1 уровня
@keyboard_router.callback_query(Pagination.filter(F.action.in_(["prev", "next"])))
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
            await callback_query.message.delete_reply_markup()
        else:
            await callback_query.answer("Please send the service list first")
    else:
        await callback_query.answer("Please send the service list first")


# Обработчик кнопок пагинации на клавиатурах 2 уровня
@keyboard_router.callback_query(F.data.in_("&button=prev"))
async def handle_back_button(callback_query: types.CallbackQuery):
    try:
        # Получаем идентификатор пользователя
        user_id = callback_query.from_user.id

        # Проверяем наличие пользователя в списке сетевых клавиатур
        if user_id in network_keyboards:
            # Получаем текущую страницу пользователя или устанавливаем 0, если пользователь новый
            current_page = current_page_dict.get(user_id, 0)

            # Уменьшаем номер страницы на 1 (возвращаемся назад)
            current_page -= 1

            # Если страница становится отрицательной, возвращаемся на последнюю страницу
            if current_page < 0:
                current_page = 0

            # Сохраняем текущую страницу пользователя
            current_page_dict[user_id] = current_page

            # Вызываем pagination_handler для отображения предыдущей страницы
            await pagination_handler(callback_query, Pagination(action="prev", page=current_page))

        else:
            await callback_query.answer("Please send the service list first")

    except Exception as e:
        print("An error occurred while handling back button:", e)


# Обработчик для кнопок соцсетей по странам на клавиатуре 2 уровня -> вывод клавиатур 3 уровня
@keyboard_router.callback_query(F.text.startswith("&secondkb"))
async def handle_second_level_to_third_countries(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        # Получение данных из состояния
        state_data = await state.get_data()

        service_list_data = state_data.get("service_list_data")
        # received_callback = state_data.get("received_callback")

        if service_list_data is None:
            print("Service list data is not available in state.")
            await callback_query.answer("Произошла ошибка. Пожалуйста, попробуйте еще раз.")
            return

        # Получаем название соцсети из callback_data
        parts = callback_query.data.split("&")
        network = None
        for part in parts:
            if part.startswith("network="):
                network = part.split("=")[1]
                break

        if network:
            # print("Нажата кнопка с коллбэком:", callback_query.data)
            # Создаем клавиатуру третьего уровня для данной соцсети и страны
            third_level_keyboard = create_third_level_keyboards(service_list_data)
            if third_level_keyboard:
                # Получаем клавиатуру третьего уровня для данной соцсети
                keyboard = third_level_keyboard.get(network.lower())
                if keyboard:
                    # Преобразуем объект Keyboa в объект InlineKeyboardMarkup
                    inline_keyboard = []
                    row = []
                    for item in keyboard.items:
                        kb_text = item['text']
                        callback_data = '&tk' + item['callback_data']
                        # print("2>3 Countries", callback_data)
                        button = InlineKeyboardButton(text=kb_text, callback_data=callback_data)
                        row.append(button)
                        if len(row) == 3 or item == keyboard.items[-1]:
                            inline_keyboard.append(row)
                            row = []

                    # Add back button
                    back_button = InlineKeyboardButton(text="⬅ Назад", callback_data="&button=prev")
                    inline_keyboard.append([back_button])

                    inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

                    # Сохраняем текущую клавиатуру в состоянии
                    await state.update_data(previous_keyboard=callback_query.message.reply_markup)
                    # Отправляем клавиатуру третьего уровня
                    await callback_query.message.edit_reply_markup(reply_markup=inline_keyboard_markup)
                else:
                    print(f"Third level keyboard for {network} not found.")
            else:
                print(f"No keyboards found for {network}.")
        else:
            print("Countries Network not found in callback data.")

    except Exception as e:
        print("2->3 lvl Countries An error occurred while handling callback query:", e)


# Обработчик для кнопок Разное на клавиатуре 2 уровня -> вывод клавиатур 3 уровня
@keyboard_router.callback_query(F.text.startswith("others"))
async def handle_second_level_to_third_others(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        # Получение данных из состояния
        state_data = await state.get_data()

        service_list_data = state_data.get("service_list_data")
        # received_callback = state_data.get("received_callback")

        if service_list_data is None:
            print("Service list data is not available in state.")
            await callback_query.answer("Произошла ошибка. Пожалуйста, попробуйте еще раз.")
            return

        # Получаем название соцсети из callback_data
        parts = callback_query.data.split(" ")
        if len(parts) >= 2:
            network = parts[1]
            # print(network)
        else:
            print("Network name not found in callback data.")
            return

        # print("Нажата кнопка с коллбэком:", callback_query.data)

        # Создаем клавиатуру третьего уровня для данной соцсети и страны
        third_level_keyboard = create_third_level_keyboards(service_list_data)

        if third_level_keyboard:
            # Получаем клавиатуру третьего уровня для данной соцсети
            keyboard = third_level_keyboard.get(network.lower())
            if keyboard:
                # Преобразуем объект Keyboa в объект InlineKeyboardMarkup
                inline_keyboard = []
                row = []
                for item in keyboard.items:
                    kb_text = item['text']
                    kb_text = kb_text[:20]
                    # print(kb_text)
                    callback_data = '&tk' + item['callback_data']
                    # print("2>3 others", callback_data)
                    button = InlineKeyboardButton(text=kb_text, callback_data=callback_data[:20])
                    # print(button)
                    row.append(button)
                    if len(row) == 3 or item == keyboard.items[-1]:
                        inline_keyboard.append(row)
                        row = []

                # Add back button
                back_button = InlineKeyboardButton(text="⬅ Назад", callback_data="&button=prev")
                inline_keyboard.append([back_button])

                inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
                # print(inline_keyboard_markup)
                # Сохраняем текущую клавиатуру в состоянии
                await state.update_data(previous_keyboard=callback_query.message.reply_markup)
                # Отправляем клавиатуру третьего уровня
                await callback_query.message.edit_reply_markup(reply_markup=inline_keyboard_markup)
            else:
                print(f"Third level keyboard for {network} not found.")
        else:
            print(f"No keyboards found for {network}.")

    except Exception as e:
        print("2->3 Others lvl An error occurred while handling callback query:", e)


# Обработчик для кнопок соцсетей на клавиатуре 1 уровня -> вывод клавиатур 3 уровня
@keyboard_router.callback_query(F.text.startswith("network"))
async def handle_first_level_to_third(callback_query: types.CallbackQuery, state: FSMContext):
    print('handle_first_level_to_third called')
    try:
        state_data = await state.get_data()

        service_list_data = state_data.get("service_list_data")
        # received_callback = state_data.get("received_callback")

        # print("received_callback:", received_callback)

        if service_list_data is None:
            print("Service list data is not available in state.")
            await callback_query.answer("Произошла ошибка. Пожалуйста, попробуйте еще раз.")
            return
        # Выводим отладочную информацию о тексте коллбэка
        # print("Нажата кнопка с коллбэком:", callback_query.data)

        network = callback_query.data.split("_")[1].lower()
        # print("Network:", network)

        third_level_keyboards = create_third_level_keyboards(service_list_data)
        if third_level_keyboards:
            third_level_keyboard = third_level_keyboards.get(network)
            if third_level_keyboard:
                await state.update_data(previous_keyboard=callback_query.message.reply_markup)
                keyboard_items = third_level_keyboard.items

                inline_keyboard = []
                for i in range(0, len(keyboard_items), 3):
                    row = []
                    for j in range(i, min(i + 3, len(keyboard_items))):
                        item = keyboard_items[j]
                        kb_text = item['text']
                        kb_text = kb_text[:20]
                        # print(kb_text)
                        callback_data = f"&tk&{item['callback_data'].split('=')[-1]}"
                        # print("1>3", callback_data)
                        button = InlineKeyboardButton(text=kb_text, callback_data=callback_data[:20])
                        row.append(button)
                        # print(button)
                    inline_keyboard.append(row)
                # print(inline_keyboard)
                back_button = InlineKeyboardButton(text="⬅ Назад", callback_data="&button=prev")
                inline_keyboard.append([back_button])

                inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

                await callback_query.message.delete_reply_markup()
                await callback_query.message.edit_reply_markup(reply_markup=inline_keyboard_markup)
            else:
                print(f"Third level keyboard for {network} not found.")
        else:
            print(f"No keyboards found for {network}.")
    except Exception as e:
        print("1->3 lvl An error occurred while handling callback query:", e)


# Обработчик для кнопок на клавиатурах 3 уровня -> вывод клавиатур 4 уровня
@keyboard_router.callback_query(F.text.startswith("&tk"))
async def handle_third_level_keyboard(callback_query: types.CallbackQuery, state: FSMContext):
    print("called handle_third_level_keyboard")
    try:
        # Получаем название категории из callback_data
        category = callback_query.data.split("&")[2]  # Получаем категорию из callback_data
        category = category.replace('%20', ' ')  # Заменяем %20 на пробелы, если есть
        category = category.lower()  # Приводим первую букву к верхнему регистру
        print("Category:", category)

        # Получаем список услуг для выбранной категории
        state_data = await state.get_data()
        service_list_data = state_data.get("service_list_data")

        if service_list_data:
            print("Creating keyboard and messages")
            messages_and_keyboards = await create_fourth_level_keyboard(service_list_data)
            print("Messages and keyboards:", messages_and_keyboards)

            if category in messages_and_keyboards:
                message_text, keyboard = messages_and_keyboards[category]
            else:
                message_text = "Клавиатура не найдена для данной категории."
                keyboard = None
        else:
            message_text = "Ошибка при получении списка услуг."
            keyboard = None

        # Отправляем сообщение с клавиатурой четвертого уровня
        await callback_query.message.edit_text(message_text, reply_markup=keyboard)

    except Exception as e:
        print("An error occurred while handling callback query for third level keyboard:", e)


# Обработчик для кнопок соцсетей на клавиатуре 1 уровня -> вывод клавиатур 2 уровня
@keyboard_router.callback_query()
async def handle_first_level_keyboard(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        # Получение данных из состояния
        state_data = await state.get_data()

        service_list_data = state_data.get("service_list_data")
        received_callback = state_data.get("received_callback")

        if service_list_data is None:
            # Если service_list_data отсутствует в состоянии, сообщаем об ошибке
            print("Service list data is not available in state.")
            await callback_query.answer("Произошла ошибка. Пожалуйста, попробуйте еще раз.")
            return

        # Получаем callback_data
        callback_data = callback_query.data
        print(callback_data)
        if callback_data.startswith("&tk"):
            await handle_third_level_keyboard(callback_query, state)

        # Проверяем, начинается ли callback_data с ожидаемого префикса
        if callback_data.startswith("network_"):
            # Извлекаем название соцсети из callback_data
            network = callback_data.split("_")[1].lower()

            # Создание второстепенных клавиатур
            second_level_keyboards = create_social_network_keyboards(service_list_data, received_callback)

            # Получаем клавиатуру второго уровня для данной соцсети
            second_level_keyboard = second_level_keyboards.get(network)
            if second_level_keyboard:
                # Сохраняем текущую клавиатуру в состоянии
                await state.update_data(previous_keyboard=callback_query.message.reply_markup)
                keyboard_items = second_level_keyboard.items  # Получаем список кнопок из объекта Keyboa

                inline_keyboard = []  # Создаем список для рядов клавиатуры

                # Добавляем кнопку "Разное" на клавиатуру второго уровня
                others_button_cb = "others " + network
                back_button = InlineKeyboardButton(text="Разное", callback_data=others_button_cb)
                # print(back_button)
                inline_keyboard.append([back_button])  # Добавляем кнопку отдельным рядом

                # Проходимся по списку кнопок и разбиваем их на ряды
                for i in range(0, len(keyboard_items), 3):
                    row = []  # Создаем пустой ряд клавиатуры
                    for j in range(i, min(i + 3, len(keyboard_items))):
                        item = keyboard_items[j]
                        kb_text = item['text']
                        callback_data = item['callback_data']
                        button = InlineKeyboardButton(text=kb_text, callback_data=callback_data)
                        row.append(button)  # Добавляем кнопку в текущий ряд
                    inline_keyboard.append(row)  # Добавляем ряд в общий список клавиатуры

                # Добавляем кнопку "⬅ Назад" на клавиатуру второго уровня
                back_button = InlineKeyboardButton(text="⬅ Назад", callback_data="&button=prev")
                inline_keyboard.append([back_button])  # Добавляем кнопку отдельным рядом

                # Создаем объект InlineKeyboardMarkup
                inline_keyboard_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

                # Удаляем клавиатуру первого уровня
                await callback_query.message.delete_reply_markup()

                # Отправляем второстепенную клавиатуру
                await callback_query.message.edit_reply_markup(reply_markup=inline_keyboard_markup)
            else:
                print(f"Second level keyboard for {network} not found.")
                await handle_first_level_to_third(callback_query, state)
        else:
            # print("Callback data does not have the expected format.")
            if callback_data.startswith("&network"):
                await handle_second_level_to_third_countries(callback_query, state)
            elif callback_data.startswith("others"):
                await handle_second_level_to_third_others(callback_query, state)

    except Exception as e:
        print("1->2 lvl An error occurred while handling callback query:", e)
