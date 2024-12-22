from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Team, TeamMember
from schemas import UserCreate, UserLogin,TokenResponse
from utils.security import create_access_token
from utils.score_calculator import update_team_score
from passlib.context import CryptContext
import secrets
import jwt
from datetime import datetime, timedelta
from routers.post import get_current_user

SECRET_KEY = "123"  # JWT 加密密鑰
ALGORITHM = "HS256"             # 加密算法

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # 檢查使用者是否已存在
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="使用者名稱已存在")

    # 創建新使用者
    hashed_password = pwd_context.hash(user.password)
    new_user = User(username=user.username, password_hash=hashed_password, created_at=datetime.utcnow())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # # 處理團隊邏輯
    # group_count = len(user.group_names)
    # if group_count == 0:
    #     raise HTTPException(status_code=400, detail="使用者必須至少加入一個團隊")
    # weight = round(1.0 / group_count, 2)  # 自動計算權重

    # for group_name in user.group_names:
    #     # 檢查團隊是否存在
    #     group = db.query(Team).filter(Team.name == group_name).first()
    #     if not group:
    #         # 如果團隊不存在，創建新團隊
    #         group = Team(name=group_name, created_at=datetime.utcnow(), score=0.0)  # 初始化 score
    #         db.add(group)
    #         db.commit()
    #         db.refresh(group)

    #     # 檢查使用者是否已加入該團隊
    #     existing_member = db.query(TeamMember).filter(
    #         TeamMember.team_id == group.id,
    #         TeamMember.user_id == new_user.id
    #     ).first()

    #     if not existing_member:
    #         # 將使用者加入團隊並設置權重
    #         team_member = TeamMember(
    #             team_id=group.id,
    #             user_id=new_user.id,
    #             weight=weight,  # 設定權重
    #             joined_at=datetime.utcnow()
    #         )
    #         db.add(team_member)

    #     # 更新隊伍分數
    #     update_team_score(group.id, db)

    db.commit()
    return {"message": "使用者已成功註冊並加入團隊"}



@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # 查詢用戶
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Username or password incorrect")

    # 返回用戶 ID
    return {"message": "Login successful", "user_id": db_user.id}



#安註記：疑似沒有用到
@router.post("/join-activity")
def join_activity(
    participation: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if participation['participation'] == "existing":
        group_name = participation['groupName']
        group = db.query(Team).filter(Team.name == group_name).first()
        if not group:
            raise HTTPException(status_code=404, detail="團隊不存在")

        team_member = TeamMember(
            team_id=group.id,
            user_id=current_user.id,
            weight=1.0,
            joined_at=datetime.utcnow()
        )
        db.add(team_member)
        db.commit()
    elif participation['participation'] == "new":
        new_group_name = participation['newGroupName']
        group = Team(name=new_group_name, created_at=datetime.utcnow(), score=0.0)
        db.add(group)
        db.commit()
        db.refresh(group)

        team_member = TeamMember(
            team_id=group.id,
            user_id=current_user.id,
            weight=1.0,
            joined_at=datetime.utcnow()
        )
        db.add(team_member)
        db.commit()
    else:
        raise HTTPException(status_code=400, detail="無效的參與方式")

    return {"message": "報名成功"}
