import psycopg2
from contextlib import contextmanager

from config_reader import config


@contextmanager
def db_connection():
    # Устанавливаем соединение с базой данных
    connection = psycopg2.connect(
        dbname=config.db_name,
        user=config.db_user,
        password=config.db_password.get_secret_value(),
        host=config.db_host
        )

    cursor = None  # Инициализируем cursor здесь

    try:
        # Создаем курсор
        cursor = connection.cursor()
        yield cursor
    finally:
        # Закрываем курсор и соединение
        cursor.close()
        connection.close()


def add_user(username, telegram_id):
    # Проверяем, существует ли уже пользователь с указанным Telegram ID
    existing_user = get_user_info(telegram_id)
    if existing_user:
        print("Пользователь уже существует в базе данных.")
        return

    # Если пользователь не существует, добавляем его в базу данных
    with db_connection() as cursor:
        try:
            cursor.execute("INSERT INTO user_profiles (telegram_id, username) VALUES (%s, %s)",
                           (telegram_id, username))
            cursor.connection.commit()
            print("Пользователь успешно добавлен в базу данных")
        except psycopg2.Error as e:
            print("Ошибка при добавлении пользователя в базу данных:", e)


def get_user_info(user_id):
    with db_connection() as cursor:
        cursor.execute("SELECT * FROM user_profiles WHERE telegram_id = %s", (user_id,))
        user_info = cursor.fetchone()
        return user_info
