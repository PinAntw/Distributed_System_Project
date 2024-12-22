from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Post, Team, User, TeamMember
from schemas import PostCreate
from datetime import datetime
import logging
import jwt
from utils.score_calculator import update_team_score

# 設定 logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SECRET_KEY = "123"  # JWT 加密密鑰
ALGORITHM = "HS256"  # 加密算法

router = APIRouter()

# 資料庫依賴函數
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 解析 Token 並提取用戶 ID
def get_current_user(authorization: str = Header(...)):
    try:
        # 確保 Authorization 欄位格式為 "Bearer <token>"
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")

        # 解析 Token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")

        logger.debug(f"Received Authorization Header: {authorization}")
        logger.debug(f"Decoded Payload: {payload}")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: Missing 'sub'")
        return user_id
    except ValueError:
        logger.error("Authorization header is invalid")
        raise HTTPException(status_code=401, detail="Invalid token format")
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        logger.error("Invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")


# 打卡 API
@router.post("/checkin", response_model=dict)
def checkin(
    post: PostCreate,
    db: Session = Depends(get_db)
):
    """
    處理使用者打卡的邏輯。
    - 檢查使用者是否加入任何團隊。
    - 為使用者加入的所有團隊新增打卡記錄。
    - 動態更新所有相關團隊的分數。
    """
    # 查找使用者加入的所有團隊
    team_memberships = db.query(TeamMember).filter(TeamMember.user_id == post.user_id).all()
    if not team_memberships:
        raise HTTPException(status_code=404, detail="使用者未加入任何團隊")

    # 為每個團隊新增打卡記錄
    for membership in team_memberships:
        new_post = Post(
            team_id=membership.team_id,
            user_id=post.user_id,
            checkin_time=datetime.utcnow(),
            post_content=post.post_content,
        )
        db.add(new_post)

        # 更新該團隊的分數
        update_team_score(membership.team_id, db)

    db.commit()

    # 獲取所有打卡的團隊及其分數
    teams_scores = db.query(Team.id, Team.name, Team.score).filter(
        Team.id.in_([membership.team_id for membership in team_memberships])
    ).all()

    return {
        "message": "打卡成功",
        "checked_in_groups": [
            {"team_id": team.id, "team_name": team.name, "team_score": team.score}
            for team in teams_scores
        ]
    }



