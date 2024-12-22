from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from database import SessionLocal
from models import Team, TeamMember, Post
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter()

# 資料庫依賴函數
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/api/ranking")
def get_top_teams(db: Session = Depends(get_db)):
    # 查詢前 20 名隊伍
    top_teams = db.query(Team).order_by(Team.score.desc()).limit(20).all()
    return {
        "top_teams": [
            {"id": team.id, "name": team.name, "score": team.score}
            for team in top_teams
        ]
    }

















# # 依賴項：獲取資料庫連接
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# # α 和 β 參數
# ALPHA = 1.5  # 時間影響權重
# BETA = 2.0   # 新會員加分
# def calculate_team_score_optimized(db: Session):
#     results = db.query(
#         Team.id.label("team_id"),
#         Team.name.label("team_name"),
#         func.sum(TeamMember.weight).label("team_size"),
#         (func.max(Post.checkin_time) - func.min(Post.checkin_time)).label("time_diff"),
#         func.count(TeamMember.id).filter(TeamMember.weight < 1.0).label("new_members")
#     ).join(TeamMember, Team.id == TeamMember.team_id).join(Post, Team.id == Post.team_id) \
#      .group_by(Team.id, Team.name).all()
    
#     rankings = []
#     for result in results:
#         team_size = result.team_size or 0
#         time_diff = result.time_diff.total_seconds() if result.time_diff else 0
#         new_members = result.new_members or 0
#         score = team_size / (ALPHA * (time_diff + 1)) + BETA * new_members
#         rankings.append({
#             "team_id": result.team_id,
#             "team_name": result.team_name,
#             "score": round(score, 2)
#         })

#     return sorted(rankings, key=lambda x: x["score"], reverse=True)[:20]

# @router.get("/api/top20")
# def get_top_20_teams(db: Session = Depends(get_db)):
#     return calculate_team_score_optimized(db)

