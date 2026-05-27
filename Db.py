from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker


database_url = "postgresql://postgres:2006@localhost:5433/group_4database"

engine = create_engine(database_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)