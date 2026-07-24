import os
from dotenv import load_dotenv

load_dotenv()


class Config:

    SERVER = os.getenv("SQL_SERVER")
    DATABASE = os.getenv("SQL_DATABASE")
    DRIVER = os.getenv("SQL_DRIVER")
    USERNAME = os.getenv("SQL_USER")
    PASSWORD = os.getenv("SQL_PASSWORD")

    required = {
        "SQL_SERVER": SERVER,
        "SQL_DATABASE": DATABASE,
        "SQL_DRIVER": DRIVER,
        "SQL_USER": USERNAME,
        "SQL_PASSWORD": PASSWORD
    }

    missing = [
        key
        for key, value in required.items()
        if not value
    ]

    if missing:
        raise RuntimeError(
            f"Faltan variables de entorno: {', '.join(missing)}"
        )

    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{USERNAME}:{PASSWORD}@"
        f"{SERVER}/{DATABASE}"
        f"?driver={DRIVER}&TrustServerCertificate=yes&charset=utf8"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False