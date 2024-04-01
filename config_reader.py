from pydantic_settings import BaseSettings
from pydantic import SecretStr
from dotenv import dotenv_values

# TO_DO: Перераспределить данные на отдельные классы (BotSettings, DBSettings, ApiSettings, etc)

# Загрузка переменных из файла .env
env_vars = dotenv_values(".env")


class Settings(BaseSettings):
    bot_token: SecretStr
    db_name: str
    db_user: str
    db_password: SecretStr
    db_host: str
    api_key: SecretStr

    class Config:
        env_file = ".env"


config = Settings(
    bot_token=SecretStr(env_vars['BOT_TOKEN']),
    db_name=env_vars['DB_NAME'],
    db_user=env_vars['DB_USER'],
    db_password=SecretStr(env_vars['DB_PASSWORD']),
    db_host=env_vars['DB_HOST'],
    api_key=SecretStr(env_vars['API_KEY'])
)
