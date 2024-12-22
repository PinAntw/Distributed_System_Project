from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, Team, TeamMember
from datetime import datetime
from utils.score_calculator import update_team_score
from schemas import CreateGroupRequest

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/groups")
def get_all_groups(db: Session = Depends(get_db)):
    """
    獲取所有現有組別。
    """
    return [{"id": group.id, "name": group.name} for group in db.query(Team).all()]


@router.post("/join-group")
def join_existing_group(
    user_id: int = Query(..., description="用戶 ID"), 
    group_id: int = Query(..., description="組別 ID"), 
    db: Session = Depends(get_db)
):
    """
    用戶加入現有組別（透過 URL Query String 傳遞參數）。
    """
    # 確保用戶存在
    existing_user = db.query(User).filter(User.id == user_id).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="用戶不存在")

    # 確保組別存在
    existing_group = db.query(Team).filter(Team.id == group_id).first()
    if not existing_group:
        raise HTTPException(status_code=404, detail="組別不存在")

    # 確保用戶尚未加入該組別
    existing_member = db.query(TeamMember).filter(
        TeamMember.user_id == user_id,
        TeamMember.team_id == group_id
    ).first()
    if existing_member:
        raise HTTPException(status_code=400, detail="用戶已經加入該組別")

    # 新增成員至組別
    new_member = TeamMember(user_id=user_id, team_id=group_id, joined_at=datetime.utcnow())
    db.add(new_member)

    db.add(existing_group)

    db.commit()
    # 更新該團隊的分數
    update_team_score(group_id, db)
    return {"message": "成功加入組別", "group_id": group_id, "user_id": user_id}


# @router.post("/create-group")
# def create_and_join_group(user_id: int, group_name: str, db: Session = Depends(get_db)):
#     print('1')
#     """
#     用戶創建新組別並自動加入。
#     """
#     # 檢查組名是否已存在
#     existing_group = db.query(Team).filter(Team.name == group_name).first()
#     if existing_group:
#         raise HTTPException(status_code=400, detail="該組別已存在")
#     print('2')
#     # 創建新組別
#     new_team = Team(name=group_name, created_at=datetime.utcnow(), score=0.0)
#     db.add(new_team)
#     db.commit()
#     db.refresh(new_team)

#     # 用戶自動加入新組別
#     new_member = TeamMember(user_id=user_id, team_id=new_team.id, joined_at=datetime.utcnow())
#     db.add(new_member)
#     db.commit()
#     # 更新該團隊的分數
#     update_team_score(new_team.id, db)
#     print('3')
#     return {"message": "成功創建並加入組別"}

@router.post("/create-group")
def create_and_join_group(request: CreateGroupRequest, db: Session = Depends(get_db)):
    user_id = request.user_id
    group_name = request.group_name

    # 檢查組名是否已存在
    existing_group = db.query(Team).filter(Team.name == group_name).first()
    if existing_group:
        raise HTTPException(status_code=400, detail="該組別已存在")

    # 創建新組別
    new_team = Team(name=group_name, created_at=datetime.utcnow(), score=0.0)
    db.add(new_team)
    db.commit()
    db.refresh(new_team)

    # 用戶自動加入新組別
    new_member = TeamMember(user_id=user_id, team_id=new_team.id, joined_at=datetime.utcnow())
    db.add(new_member)
    db.commit()

    # 更新該團隊的分數
    update_team_score(new_team.id, db)
    return {"message": "成功創建並加入組別"}
