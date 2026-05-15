import os

class Config:
    SERVER = os.getenv("SQL_SERVER", "localhost\\SQLEXPRESS")
    DATABASE = os.getenv("SQL_DATABASE", "ElImperioDeLosBolsos")
    DRIVER = os.getenv("SQL_DRIVER", "ODBC Driver 17 for SQL Server")
    USERNAME = os.getenv("SQL_USER", "sa")
    PASSWORD = os.getenv("SQL_PASSWORD", "1234")
    
    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{USERNAME}:{PASSWORD}@"
        f"{SERVER}/{DATABASE}"
        f"?driver={DRIVER}&TrustServerCertificate=yes&charset=utf8"
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False