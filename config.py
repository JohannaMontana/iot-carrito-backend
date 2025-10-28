import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Configuración de RDS MySQL
    DB_HOST = os.getenv('DB_HOST', 'tu-rds-endpoint.rds.amazonaws.com')
    DB_USER = os.getenv('DB_USER', 'admin')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'tu-password')
    DB_NAME = os.getenv('DB_NAME', 'iot_monitor')
    DB_PORT = int(os.getenv('DB_PORT', 3306))

    # Configuración Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave-secreta-iot')
    DEBUG = os.getenv('DEBUG', False)

    # WebSocket
    SOCKETIO_ASYNC_MODE = 'eventlet'