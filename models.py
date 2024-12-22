from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, Float, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import DateTime

# User 資料表

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 關聯到 Post
    posts = relationship("Post", back_populates="user")

    # 關聯到 TeamMember
    team_members = relationship("TeamMember", back_populates="user")



class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # 新增分數欄位
    score = Column(Float, default=0.0)  
    
    # 關聯到 Post
    posts = relationship("Post", back_populates="team")
    # 關聯到 TeamMember
    members = relationship("TeamMember", back_populates="team")





class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    weight = Column(Float, default=1.0)
    joined_at = Column(DateTime, default=datetime.utcnow)

    # 關聯到 Team 和 User
    team = relationship("Team", back_populates="members")
    user = relationship("User", back_populates="team_members")


# Post 資料表（打卡記錄表）
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    post_content = Column(String, nullable=False)
    checkin_time = Column(DateTime, default=datetime.utcnow)

    # 關聯到 Team 和 User
    team = relationship("Team", back_populates="posts")
    user = relationship("User", back_populates="posts")

