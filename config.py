"""
FunPay Autopilot - Global Configuration
"""
import os
from pydantic_settings import BaseSettings


class BackendConfig(BaseSettings):
    APP_NAME: str = "FunPay Autopilot"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = os.getenv("FPA_SECRET_KEY", "change-me-in-production")
    DATABASE_URL: str = "sqlite+aiosqlite:///./funpay_autopilot.db"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WS_PING_INTERVAL: int = 30
    TRIAL_DAYS: int = 7

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = os.getenv("FPA_BOT_TOKEN", "")

    # Tariff prices (in Telegram Stars)
    START_PRICE_STARS: int = 120
    MEDIUM_PRICE_STARS: int = 300
    MAX_PRICE_STARS: int = 700

    class Config:
        env_prefix = "FPA_"
        env_file = ".env"


class WorkerConfig(BaseSettings):
    """Config for Windows Worker"""
    BACKEND_URL: str = "http://localhost:8000"
    WS_URL: str = "ws://localhost:8000/ws"
    DEVICE_NAME: str = "Windows Worker"
    APP_VERSION: str = "1.0.0"
    CHECK_INTERVAL_SEC: int = 60
    MAX_RETRIES: int = 3

    class Config:
        env_prefix = "FPA_WORKER_"


backend_config = BackendConfig()
worker_config = WorkerConfig()
