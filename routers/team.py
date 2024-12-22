from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Team, TeamMember, User
from pydantic import BaseModel

router = APIRouter()

# 依賴：獲取資料庫連線
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 請求格式定義
class TeamCreate(BaseModel):
    name: str

class TeamJoin(BaseModel):
    team_id: int
    user_id: int
    weight: float = 1.0  # 預設權重

# 1. 創建團隊
@router.post("/create", response_model=dict)
def create_team(team: TeamCreate, db: Session = Depends(get_db)):
    # 檢查團隊名稱是否已存在
    existing_team = db.query(Team).filter(Team.name == team.name).first()
    if existing_team:
        raise HTTPException(status_code=400, detail="Team name already exists")
    
    # 創建新團隊
    new_team = Team(name=team.name)
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    return {"message": "Team created successfully", "team_id": new_team.id}

# 2. 新增團隊成員
@router.post("/join", response_model=dict)
def join_team(team_join: TeamJoin, db: Session = Depends(get_db)):
    # 檢查團隊是否存在
    team = db.query(Team).filter(Team.id == team_join.team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # 檢查使用者是否存在
    user = db.query(User).filter(User.id == team_join.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 檢查使用者是否已經加入該團隊
    existing_member = db.query(TeamMember).filter(
        TeamMember.team_id == team_join.team_id,
        TeamMember.user_id == team_join.user_id
    ).first()
    if existing_member:
        raise HTTPException(status_code=400, detail="User already in the team")
    
    # 加入團隊
    new_member = TeamMember(
        team_id=team_join.team_id,
        user_id=team_join.user_id,
        weight=team_join.weight
    )
    db.add(new_member)
    db.commit()
    return {"message": "User added to team successfully"}
