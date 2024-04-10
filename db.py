import psycopg2
import asyncpg
import tracemalloc

from contextlib import contextmanager
from config_reader import config


@contextmanager
def db1_connection():
    # Устанавливаем соединение с базой данных
    connection = psycopg2.connect(
        dbname=config.db1_name,
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
    with db1_connection() as cursor:
        try:
            cursor.execute("INSERT INTO user_profiles (telegram_id, username) VALUES (%s, %s)",
                           (telegram_id, username))
            cursor.connection.commit()
            print("Пользователь успешно добавлен в базу данных")
        except psycopg2.Error as e:
            print("Ошибка при добавлении пользователя в базу данных:", e)


def get_user_info(user_id):
    with db1_connection() as cursor:
        cursor.execute("SELECT * FROM user_profiles WHERE telegram_id = %s", (user_id,))
        user_info = cursor.fetchone()
        return user_info


tracemalloc.start()


@contextmanager
def db2_connection():
    # Устанавливаем соединение с базой данных
    connection = psycopg2.connect(
        dbname=config.db2_name,
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


async def add_services(service_list_data):
    print("add_services called")
    conn = await asyncpg.connect(
        user=config.db_user,
        password=config.db_password.get_secret_value(),
        database=config.db2_name,
        host=config.db_host
    )
    try:
        async with conn.transaction():
            for service_data in service_list_data:
                await conn.execute("""
                    INSERT INTO services (service_id, name, type, rate, min, max, dripfeed, refill, cancel, category) 
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                    service_data['service'],
                    service_data['name'],
                    service_data['type'],
                    float(service_data['rate']),
                    int(service_data['min']),
                    int(service_data['max']),
                    service_data['dripfeed'],
                    service_data['refill'],
                    service_data['cancel'],
                    service_data['category']
                )

        print("Данные успешно добавлены в базу данных")
    finally:
        await conn.close()


async def get_order_type_by_service_id(service_id):
    query = "SELECT type FROM services WHERE id = $1"
    try:
        conn = await asyncpg.connect(
            user=config.db_user,
            password=config.db_password.get_secret_value(),
            database=config.db2_name,
            host=config.db_host
        )
        row = await conn.fetchrow(query, service_id)
        return row['type'] if row else None
    finally:
        if conn:
            await conn.close()