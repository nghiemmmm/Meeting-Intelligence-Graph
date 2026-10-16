from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.api.routes.health import router as health_router
from src.api.routes.meetings import router as meetings_router
from src.api.routes.actions import router as actions_router
from src.api.routes.decisions import router as decisions_router
from src.api.routes.insights import router as insights_router
from src.api.routes.graph import router as graph_router
from src.db import init_db

# Khởi tạo các bảng SQLite (data/meetings.db)
init_db()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    ## 🚀 Meeting Intelligence Assistant Backend API
    Hệ thống biến biên bản cuộc họp thành dữ liệu có cấu trúc có thể tiếp tục sử dụng:
    * **5 Nhóm dữ liệu cốt lõi**: Quyết định, Công việc, Vướng mắc, Yêu cầu/Phản hồi, Nội dung chưa chốt.
    * **Temporal Decision Tracking**: Theo dõi sự thay đổi quyết định theo thời gian (`SUPERSEDES`).
    * **Evidence-Centered Meeting Knowledge Graph**: Xây dựng đồ thị tri thức với liên kết bằng chứng gốc.
    * **Graph Retrieval**: Truy vấn chuỗi nhân quả và kiểm toán quyết định qua Graph Traversal.
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Cấu hình CORS cho phép Frontend / Client kết nối
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các Router
app.include_router(health_router)
app.include_router(meetings_router)
app.include_router(actions_router)
app.include_router(decisions_router)
app.include_router(insights_router)
app.include_router(graph_router)

import os
from fastapi.staticfiles import StaticFiles

# Mount Frontend Web SPA nếu đã build dist
frontend_dist = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
else:
    @app.get("/")
    def root():
        return {
            "message": "Welcome to Meeting Intelligence Assistant API",
            "docs_url": "/docs",
            "health": "/health"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
