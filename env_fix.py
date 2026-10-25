import os

SECRET_KEY = os.getenv("ARKHE_SECRET")
if not SECRET_KEY:
    raise RuntimeError("FATAL DE SEGURIDAD: La variable de entorno ARKHE_SECRET no está definida. El sistema no arrancará sin su llave cr