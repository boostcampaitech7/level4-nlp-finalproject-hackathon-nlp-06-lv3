import os

from databases import Database

# MySQL 연결 URL (환경 변수나 .env로 관리하는 것이 좋음)
DATABASE_URL = (
    f"mysql+aiomysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@localhost:3307"
    f"/{os.getenv('MYSQL_DATABASE')}"
)

# Database 객체 생성
database = Database(DATABASE_URL)
