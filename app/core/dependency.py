from app.core.database_postgres import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    
    finally:
        db.close()
 