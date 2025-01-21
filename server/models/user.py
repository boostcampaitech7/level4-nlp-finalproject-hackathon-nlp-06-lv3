from sqlalchemy import TIMESTAMP, Column, Integer, String
from sqlalchemy.sql import func

from server.database.connection import Base


class User(Base):
    __tablename__ = "user_tb"  # 테이블 이름

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)  # 기본 키, AUTO_INCREMENT
    name = Column(String(20), nullable=False)  # 이름
    email = Column(String(255), unique=True, nullable=False)  # 이메일
    google_id = Column(String(50), unique=True, nullable=False)  # Google ID
    profile_url = Column(String(255), nullable=False)  # 프로필 URL
    access_token = Column(String(255), nullable=False)  # 액세스 토큰
    refresh_token = Column(String(255), nullable=False)  # 리프레시 토큰
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())  # 생성 시간, DEFAULT CURRENT_TIMESTAMP
