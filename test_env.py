# backend/test_env.py
from dotenv import load_dotenv
import os

# Cargar variables del .env
load_dotenv()

print("=== VERIFICANDO CONFIGURACIÓN ===")
print(f"DB_HOST: {os.getenv('DB_HOST')}")
print(f"DB_USER: {os.getenv('DB_USER')}")
print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD')}")
print(f"DB_NAME: {os.getenv('DB_NAME')}")
print(f"DB_PORT: {os.getenv('DB_PORT')}")

# Probar conexión a la base de datos
try:
    import pymysql
    connection = pymysql.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        port=int(os.getenv('DB_PORT'))
    )
    print("✅ CONEXIÓN A RDS EXITOSA!")
    connection.close()
except Exception as e:
    print(f"❌ ERROR DE CONEXIÓN: {e}")