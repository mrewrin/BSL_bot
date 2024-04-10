# class InputTypeMiddleware(BaseMiddleware):
#     async def __call__(
#             self,
#             handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
#             event: TelegramObject,
#             data: Dict[str, Any]
#     ) -> Any:
#         if isinstance(event, Message):  # Проверяем, является ли событие сообщением
#             message = event  # Приводим событие к типу Message
#             if message.text.isdigit():
#                 data['input_type'] = 'number'
#             elif message.text.startswith('http'):
#                 data['input_type'] = 'link'
#
#         # Вызываем обработчик, передавая ему модифицированное событие и данные
#         result = await handler(event, data)
#         return result