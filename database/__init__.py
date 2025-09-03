from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.base import Base
from database.models import Project, Shop, Product

from env_settings import EnvSettings, BASE_DIR

settings = EnvSettings()

if settings.USE_SQLITE:
    engine = create_engine(f"sqlite+pysqlite:///{BASE_DIR / settings.DB_NAME}.sqlite", echo=True, future=True)
else:
    engine = create_engine(
        f"mariadb+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}//{settings.DB_NAME}",
        echo=True, future=True
    )

if __name__ == '__main__':
    Base.metadata.create_all(engine)

# 創建會話工廠
Session = sessionmaker(bind=engine)
