from fastapi import FastAPI, Request
from database import Base, engine
from routers import auth, post, ranking, group
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import os

# 初始化 FastAPI
app = FastAPI()

# 初始化資料庫
def init_db():
    # 確保資料表在應用啟動時被正確建立
    Base.metadata.create_all(bind=engine)

# 掛載路由
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(post.router, prefix="/post", tags=["Post"])
app.include_router(ranking.router, prefix="/ranking", tags=["Ranking"])
app.include_router(group.router, prefix="/api/groups", tags=["groups"])


# 掛載靜態檔案
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 基本頁面路由
@app.get("/", response_class=HTMLResponse)
def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
def read_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/checkin", response_class=HTMLResponse)
def read_checkin(request: Request):
    return templates.TemplateResponse("checkin.html", {"request": request})

@app.get("/ranking", response_class=HTMLResponse)
def read_ranking(request: Request):
    return templates.TemplateResponse("ranking.html", {"request": request})

@app.get("/activity", response_class=HTMLResponse)
def read_ranking(request: Request):
    return templates.TemplateResponse("activity.html", {"request": request})

# 啟動 FastAPI 應用程式並監聽 PORT
if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 8080))  # 從環境變數取得 PORT，預設為 8080
    uvicorn.run(app, host="0.0.0.0", port=port)
