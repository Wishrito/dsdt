from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Starboard(Base):
    __tablename__ = 'starboards'

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(Integer, nullable=False, unique=True)
    emoji_name = Column(String, nullable=False, unique=True)
    emoji_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<Starboard(id={self.id}, channel_id={self.channel_id}, emoji_name={self.emoji_name}, star_count={self.emoji_count})>"

class StarboardContent(Base):
    __tablename__ = "starboard_content"

    id = Column(Integer, primary_key=True)
    starboard_id = Column(Integer, nullable=False)
    emoji_count = Column(Integer, default=0)

    def vote(self):
        self.emoji_count += 1
        return self.emoji_count

    def unvote(self):
        if self.emoji_count > 0:
            self.emoji_count -= 1
        return self.emoji_count

    def __repr__(self):
        return f"<StarboardImage(id={self.id}, starboard_id={self.starboard_id}, image_message_id={self.image_message_id})>"

# Configuration de la base de données
engine = create_engine("sqlite:///sdt.db", echo=True)
Base.metadata.create_all(engine)
