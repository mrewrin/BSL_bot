# from typing import Any, Awaitable, Callable, Dict
from aiogram import Router, types
from aiogram.types import ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
# from aiogram.fsm.storage.memory import MemoryStorage
# from aiogram.types import Message, TelegramObject

from ..api_client import *
# from ..db import *


ord_router = Router()


# Одиночный заказ
class Order:
    def __init__(self, service_id: int, link: str, quantity: int, runs: int = None, interval: int = None):
        self.service_id = service_id
        self.link = link
        self.quantity = quantity
        self.runs = runs
        self.interval = interval

    def to_dict(self):
        return {
            'service_id': self.service_id,
            'link': self.link,
            'quantity': self.quantity,
            'runs': self.runs,
            'interval': self.interval
        }


# Определение состояний FSM
# Родительский класс состояний формы заказа
class OrderFormBase(StatesGroup):
    get_service_id = State()
    get_link = State()
    get_quantity = State()


# Дочерний класс состояний FSM для заказов типа "Default"
class OrderFormDefault(OrderFormBase):
    get_service_id = State()
    get_link = State()
    get_quantity = State()
    get_runs = State()
    get_interval = State()


# Дочерний класс состояний FSM для заказов типа "Package"
class OrderFormPackage(OrderFormBase):
    get_service_id = State()
    get_link = State()


# Дочерний класс состояний FSM для заказов типа "Custom Comments"
class OrderFormCustomComments(OrderFormBase):
    get_service_id = State()
    get_link = State()
    get_comments = State()


# Дочерний класс состояний FSM для заказов типа "Mentions"
class OrderFormMentions(OrderFormBase):
    get_service_id = State()
    get_link = State()
    get_quantity = State()
    get_usernames = State()


# Дочерний класс состояний FSM для заказов типа "Mentions with Hashtags"
class OrderFormMentionsWithHashtags(OrderFormBase):
    get_service_id = State()
    get_link = State()
    get_quantity = State()
    get_usernames = State()
    get_hashtags = State()


# Дочерний класс состояний FSM для заказов типа "Mentions Custom List"
class OrderFormMentionsCustomList(OrderFormBase):
    get_service_id = State()
    get_link = State()
    get_usernames = State()


# Дочерний класс состояний FSM для заказов типа "Mentions Hashtag"
class OrderFormMentionsHashtag(OrderFormBase):
    get_service_id = State()
    get_link = State()
    get_quantity = State()
    get_hashtag = State()


# Дочерний класс состояний FSM для заказов типа "Mentions User Followers"
class OrderFormMentionsUserFollowers(OrderFormBase):
    get_service_id = State()
    get_link = State()
    get_quantity = State()
    get_username = State()


# Дочерний класс состояний FSM для заказов типа "Mentions Media Likers"
class OrderFormMentionsMediaLikers(OrderFormBase):
    get_service_id = State()
    get_link = State()
    get_quantity = State()
    get_media = State()


# Дочерний класс состояний FSM для заказов типа "Custom Comments Package"
class OrderFormCustomCommentsPackage(OrderFormBase):
    get_service_id = State()
    get_link = State()
    get_comments = State()


# Дочерний класс состояний FSM для заказов типа "Comment Likes"
class OrderFormCommentLikes(OrderFormBase):
    get_service_id = State()
    get_link = State()
    get_quantity = State()
    get_username = State()


# Дочерний класс состояний FSM для заказов типа "Poll"
class OrderFormPoll(OrderFormBase):
    get_service_id = State()
    get_link = State()
    get_quantity = State()
    get_answer_number = State()


# Дочерний класс состояний FSM для заказов типа "Invites from Groups"
class OrderFormInvitesFromGroups(OrderFormBase):
    get_service_id = State()
    get_link = State()
    get_quantity = State()
    get_groups = State()


# Дочерний класс состояний FSM для заказов типа "Subscriptions"
class OrderFormSubscriptions(OrderFormBase):
    get_service_id = State()
    get_username = State()
    get_min_quantity = State()
    get_max_quantity = State()
    get_posts = State()
    get_old_posts = State()
    get_delay = State()
    get_expiry = State()


# order_types = ['Default', 'Package', 'Custom Сomments', 'Mentions',
#                'Mentions with Hashtags', 'Mentions Custom List',
#                'Mentions Hashtag', 'Mentions User Followers',
#                'Mentions Media Likers', 'Custom Comments Package',
#                'Comment Likes', 'Poll', 'Invites from Groups', 'Subscriptions']


@ord_router.message(Command("order"))
async def start_order(message: types.Message, state: FSMContext):
    print("start_order called")
    await state.set_state(OrderFormBase.get_service_id)
    await message.answer("Введите идентификатор услуги:",
                         reply_markup=ReplyKeyboardRemove(),
                         )


@ord_router.message(OrderFormBase.get_service_id)
async def process_service_id(message: types.Message, state: FSMContext):
    await state.update_data(get_service_id=message.text)
    await state.set_state(OrderFormBase.get_link)
    await message.answer("Пожалуйста, введите ссылку на пост или аккаунт:",
                         reply_markup=ReplyKeyboardRemove(),
                         )


@ord_router.message(OrderFormBase.get_link)
async def process_link_default(message: types.Message, state: FSMContext):
    await state.update_data(get_link=message.text)
    await state.set_state(OrderFormBase.get_quantity)
    await message.answer("Пожалуйста, введите количество:",
                         reply_markup=ReplyKeyboardRemove(),
                         )


@ord_router.message(OrderFormBase.get_quantity)
async def process_quantity(message: types.Message, state: FSMContext):
    await state.update_data(get_quantity=message.text)
    data = await state.get_data()
    service_id = data['get_service_id']
    link = data['get_link']
    quantity = data['get_quantity']

    # Создаем экземпляр класса Order
    order = Order(service_id=service_id, link=link, quantity=quantity)

    # Вызываем функцию add_order и передаем ей данные заказа
    await add_order_default(user_api_key, order.service_id, order.link, order.quantity)

    # Сбрасываем состояние FSM
    await state.clear()
    await message.answer("Заказ успешно добавлен",
                         reply_markup=ReplyKeyboardRemove()
                         )


class OrderStatusStates(StatesGroup):
    waiting_for_order_id = State()


@ord_router.message(Command("order_status"))
async def order_status(message: types.Message, state=FSMContext):
    await state.set_state(OrderStatusStates.waiting_for_order_id)
    await message.answer("Введите ID заказа:")


@ord_router.message(OrderStatusStates.waiting_for_order_id)
async def process_order_id(message: types.Message, state=FSMContext):
    await state.update_data(waiting_for_order_id=message.text)
    data = await state.get_data()
    order_id = data['waiting_for_order_id']
    # Получаем статус заказа
    status_of_order = await get_order_status(user_api_key, order_id)

    # Проверяем результат
    if status_of_order:
        await message.answer(f"Статус вашего заказа (ID {order_id}): {status_of_order}")
    else:
        await message.answer(f"Не удалось получить информацию о статусе заказа (ID {order_id}). "
                             f"Пожалуйста, попробуйте позже.")
