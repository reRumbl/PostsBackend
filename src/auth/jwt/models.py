from datetime import datetime
from sqlalchemy.orm import Mapped
from src.database import Base


class BlackListTokenModel(Base):
    __tablename__ = 'black_list_token'
    
    expire: Mapped[datetime]
