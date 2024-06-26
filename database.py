# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://admin:1234@postgresql:5432/db_modelos"
#SQLALCHEMY_DATABASE_URL = "postgresql://administrador:proyectoML%@basedatospostgres.postgres.database.azure.com:5432/db_modelos"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
