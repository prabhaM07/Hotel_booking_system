from sqlalchemy import (Column,Integer,String,DateTime,ForeignKey,func,UniqueConstraint,CheckConstraint)
from sqlalchemy.orm import relationship
from app.core.database_postgres import Base


class TokenStore(Base):
    __tablename__ = "token_store"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    access_token = Column(String(512), nullable=False, unique=True)
    refresh_token = Column(String(512), nullable=False, unique=True)
    
    access_token_expiry = Column(DateTime(timezone=True), nullable=False)
    refresh_token_expiry = Column(DateTime(timezone=True), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("Users", back_populates="token", lazy="joined")

    __table_args__ = (
        UniqueConstraint("user_id", "refresh_token", name="uq_user_refresh_token"),
        CheckConstraint("char_length(access_token) > 10", name="check_access_token_length"),
        CheckConstraint("char_length(refresh_token) > 10", name="check_refresh_token_length"),
    )
