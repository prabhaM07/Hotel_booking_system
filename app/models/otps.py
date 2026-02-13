from sqlalchemy import JSON, Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from app.core.database_postgres import Base 

def default_expiry():
    return datetime.now() + timedelta(minutes=5)

class OTPModel(Base):
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True,autoincrement=True, index=True)
    email = Column(String, nullable=False, index=True)
    otp = Column(String, nullable=False)
    temp_user_data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expiry = Column(DateTime(timezone=True), default=default_expiry)

    def __repr__(self):
        return f"<OTP(email={self.email}, otp={self.otp}, expiry={self.expiry})>"
