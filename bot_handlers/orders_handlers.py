from typing import Any, Awaitable, Callable, Dict
from aiogram import Router, types, F, BaseMiddleware
from aiogram.types import ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, TelegramObject

from ..api_client import *

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
class OrderForm(StatesGroup):
    get_service_id = State()
    get_link = State()
    get_quantity = State()
    get_runs = State()
    get_interval = State()


@ord_router.message(Command("order"))
async def start_order(message: types.Message, state: FSMContext):
    print("start_order called")
    await state.set_state(OrderForm.get_service_id)
    await message.answer("Введите идентификатор услуги:",
                         reply_markup=ReplyKeyboardRemove(),
                         )


@ord_router.message(OrderForm.get_service_id)
async def process_service_id(message: types.Message, state: FSMContext):
    await state.update_data(get_service_id=message.text)
    await state.set_state(OrderForm.get_link)
    await message.answer("Пожалуйста, введите ссылку на пост или аккаунт:",
                         reply_markup=ReplyKeyboardRemove(),
                         )


@ord_router.message(OrderForm.get_link)
async def process_link(message: types.Message, state: FSMContext):
    await state.update_data(get_link=message.text)
    await state.set_state(OrderForm.get_quantity)
    await message.answer("Пожалуйста, введите количество:",
                         reply_markup=ReplyKeyboardRemove(),
                         )


@ord_router.message(OrderForm.get_quantity)
async def process_quantity(message: types.Message, state: FSMContext):
    await state.update_data(get_quantity=message.text)
    data = await state.get_data()
    service_id = data['get_service_id']
    link = data['get_link']
    quantity = data['get_quantity']

    # Создаем экземпляр класса Order
    order = Order(service_id=service_id, link=link, quantity=quantity)

    # Вызываем функцию add_order и передаем ей данные заказа
    await add_order_default(api_key, order.service_id, order.link, order.quantity)

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
    status_of_order = await get_order_status(api_key, order_id)

    # Проверяем результат
    if status_of_order:
        await message.answer(f"Статус вашего заказа (ID {order_id}): {status_of_order}")
    else:
        await message.answer(f"Не удалось получить информацию о статусе заказа (ID {order_id}). "
                             f"Пожалуйста, попробуйте позже.")
