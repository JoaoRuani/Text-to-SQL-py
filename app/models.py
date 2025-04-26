from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    connection_strings = relationship("ConnectionString", back_populates="owner")

class ConnectionString(Base):
    __tablename__ = "connection_strings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    connection_string = Column(Text)
    database_type = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="connection_strings") 