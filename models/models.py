from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, TIMESTAMP
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

Base = declarative_base()


class Users(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    username: str = Column(String, nullable=True, unique=True)
    email: str = Column(String, nullable=True, unique=True)
    register_data: datetime.utcnow = Column(TIMESTAMP, default=datetime.utcnow())
    hashed_password: str = Column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
