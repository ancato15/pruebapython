import os
from urllib.parse import urlparse, unquote
import pymysql


def conectar():
    url = os.environ.get("DATABASE_URL")
    if url:
        u = urlparse(url)
        return pymysql.connect(
            host=u.hostname,
            port=u.port or 3306,
            user=unquote(u.username or ""),
            password=unquote(u.password or ""),
            database=u.path.lstrip("/"),
            charset="utf8mb4",
        )

    # Desarrollo local
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "12345678"),
        database=os.getenv("DB_NAME", "veterinaria"),
        port=int(os.getenv("DB_PORT", "3307")),
        charset="utf8mb4",
    )