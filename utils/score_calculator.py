from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import Team, TeamMember, Post


# 假設這些權重參數是固定的，您也可以根據需求動態調整
ALPHA = 0.0001 # 時間差的權重
BETA = 3   # 新會員的權重

def calculate_team_score(team_id: int, db: Session) -> float:
    print('------------------------------------------')
    # 取得團隊所有成員
    team_members = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()
    if not team_members:
        return 0.0  # 如果團隊沒有成員，分數為 0

    # 計算 T：加總所有成員的權重
    total= len(team_members)

    # 取得該團隊所有打卡記錄
    checkins = db.query(Post).filter(Post.team_id == team_id).all()
    if not checkins:
        return 0.0  # 如果沒有打卡記錄，分數為 0

    # 計算 S：時間差（最後一個打卡時間 - 第一個打卡時間）
    checkin_times = [checkin.checkin_time for checkin in checkins]
    time_diff = (max(checkin_times) - min(checkin_times)).total_seconds() / 3600  # 換算成小時

    # 計算 N：新會員數量（加入時間在最近 7 天內）
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    new_members_count = sum(1 for member in team_members if member.joined_at >= one_week_ago)

    # 套用公式計算團隊分數
    team_score = total/ (ALPHA * (time_diff + 1)) + BETA * new_members_count

    # 四捨五入到小數點後兩位
    return round(team_score, 2)


def update_team_score(team_id: int, db: Session):
    print('+++++++++++++++++++++++++++++++++++++++')
    team_score = calculate_team_score(team_id, db)
    team = db.query(Team).filter(Team.id == team_id).first()
    if team:
        team.score = team_score
        print(team_score)
        db.commit()
