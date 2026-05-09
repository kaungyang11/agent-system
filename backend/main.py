"""
代理商销售管理系统 - 后端 API
Python FastAPI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from app.database import init_db

app = FastAPI(
    title="代理商销售管理系统",
    description="算能代理商销售管理后端API",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>代理商销售管理系统</title>
        </head>
        <body>
            <h1>🚀 系统运行中</h1>
            <p>后端API服务已启动</p>
            <p>访问 /docs 查看API文档</p>
        </body>
    </html>
    """


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "message": "服务运行正常"}


# ============ 导入各模块路由 ============
from app.routers import auth, users, products, agents, orders, inventory, customers, performance

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(inventory.router, prefix="/api/v1")
app.include_router(customers.router, prefix="/api/v1")
app.include_router(performance.router, prefix="/api/v1")


# 启动时初始化数据库
@app.on_event("startup")
async def startup_event():
    init_db()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)