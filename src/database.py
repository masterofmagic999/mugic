"""
Database models and initialization
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship

Base = declarative_base()


class Piece(Base):
    """Music piece model"""
    __tablename__ = 'pieces'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    analysis = Column(Text, nullable=False)  # JSON string
    upload_date = Column(DateTime, nullable=False)
    
    # Relationship to practice sessions
    sessions = relationship('PracticeSession', back_populates='piece', cascade='all, delete-orphan')


class PracticeSession(Base):
    """Practice session model"""
    __tablename__ = 'practice_sessions'
    
    id = Column(Integer, primary_key=True)
    piece_id = Column(Integer, ForeignKey('pieces.id'), nullable=False)
    audio_analysis = Column(Text, nullable=False)  # JSON string
    feedback = Column(Text, nullable=False)  # JSON string
    instrument = Column(String(100), nullable=False)
    score = Column(Integer, nullable=False)
    session_date = Column(DateTime, nullable=False)
    
    # Relationship to piece
    piece = relationship('Piece', back_populates='sessions')


# Database setup
db_path = os.path.join(os.path.dirname(__file__), '..', 'mugic.db')
engine = create_engine(f'sqlite:///{db_path}', echo=False)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base.query = db_session.query_property()


def init_db():
    """Initialize the database"""
    Base.metadata.create_all(bind=engine)
