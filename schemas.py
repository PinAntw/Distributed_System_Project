from pydantic import BaseModel
from datetime import datetime
from typing import List

class UserCreate(BaseModel):
    username: str
    password: str
    # group_names: List[str]  # 新增要加入的團隊名稱，可以是新的或現有的

class UserLogin(BaseModel):
    username: str
    password: str


class PostCreate(BaseModel):
    user_id: int
    post_content: str

# 登入回應格式（回傳 Token）
class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# 安新增：創建隊伍改成不用url傳遞
class CreateGroupRequest(BaseModel):
    user_id: int
    group_name: str