from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# DATABASE_URL = "postgresql://postgres:dis@34.57.64.54:5432/postgres"
#an's db
DATABASE_URL = "postgresql://disdbuser:dis@35.236.174.84:5432/disdatabase"



engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# 安全創建資料表
def init_db():
    Base.metadata.create_all(bind=engine, checkfirst=True)
