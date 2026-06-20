"""
ReplayMind Backend Application
基于多模态AI与RAG的游戏录像智能复盘系统
"""

import os
import sys

def _fix_windows_ssl_cert_store():
    """
    修复 Windows 平台下 ssl.create_default_context() 加载 Windows 证书存储时
    因证书数据损坏而抛出 SSLError: [ASN1: NOT_ENOUGH_DATA] not enough data 的问题。

    采用两级防御：
      1) 将 SSL_CERT_FILE / REQUESTS_CA_BUNDLE 指向 certifi 的 CA bundle，
         为尊重该环境变量的库（如 requests、urllib3、aiohttp 运行时）提供可用根证书。
      2) 对 ssl.SSLContext 的 load_default_certs / _load_windows_store_certs 做
         monkey-patch，捕获读取 Windows 证书存储时抛出的 ssl.SSLError，
         并退回到 certifi 的 cacert.pem，保证 aiohttp 在 import 时能正常完成初始化。
    """
    if sys.platform != "win32":
        return

    # ---- 1) 定位 certifi CA bundle 并设置环境变量 ----
    cert_file = None
    try:
        import certifi  # type: ignore
        cert_file = certifi.where()
    except Exception:
        pass
    if cert_file is None or not os.path.isfile(cert_file):
        for base in (os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Python"),
                     os.path.join(os.environ.get("PROGRAMFILES", ""), "Python"),
                     os.path.dirname(sys.executable)):
            if not base:
                continue
            p = os.path.join(base, "Lib", "site-packages", "certifi", "cacert.pem")
            if os.path.isfile(p):
                cert_file = p
                break
    if cert_file and os.path.isfile(cert_file) and not os.environ.get("SSL_CERT_FILE"):
        os.environ["SSL_CERT_FILE"] = cert_file
        os.environ["REQUESTS_CA_BUNDLE"] = cert_file

    # ---- 2) 对 ssl.SSLContext 做 monkey-patch 以捕获 Windows 证书存储读取错误 ----
    import ssl

    _orig_load_default_certs = ssl.SSLContext.load_default_certs
    _orig_load_windows_store_certs = getattr(ssl.SSLContext, "_load_windows_store_certs", None)
    _orig_create_default_context = ssl.create_default_context
    _fallback_cafile = cert_file  # 捕获异常时退回到的证书 bundle

    def _safe_load_default_certs(self, purpose=ssl.Purpose.SERVER_AUTH):
        try:
            _orig_load_default_certs(self, purpose)
        except ssl.SSLError:
            if _fallback_cafile and os.path.isfile(_fallback_cafile):
                try:
                    self.load_verify_locations(_fallback_cafile)
                except Exception:
                    pass

    def _safe_load_windows_store_certs(self, storename, purpose):
        if _orig_load_windows_store_certs is None:
            return
        try:
            _orig_load_windows_store_certs(self, storename, purpose)
        except ssl.SSLError:
            # Windows 证书存储中存在损坏条目，忽略并降级到 certifi bundle
            if _fallback_cafile and os.path.isfile(_fallback_cafile):
                try:
                    self.load_verify_locations(_fallback_cafile)
                except Exception:
                    pass
        except OSError:
            pass

    def _safe_create_default_context(purpose=ssl.Purpose.SERVER_AUTH, *, cafile=None,
                                      capath=None, cadata=None):
        if cafile is None and capath is None and cadata is None \
                and _fallback_cafile and os.path.isfile(_fallback_cafile):
            cafile = _fallback_cafile
        try:
            return _orig_create_default_context(purpose, cafile=cafile, capath=capath, cadata=cadata)
        except ssl.SSLError:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            if _fallback_cafile and os.path.isfile(_fallback_cafile):
                try:
                    ctx.load_verify_locations(_fallback_cafile)
                except Exception:
                    pass
            return ctx

    ssl.SSLContext.load_default_certs = _safe_load_default_certs
    if _orig_load_windows_store_certs is not None:
        ssl.SSLContext._load_windows_store_certs = _safe_load_windows_store_certs
    ssl.create_default_context = _safe_create_default_context

_fix_windows_ssl_cert_store()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from common import settings, logger
from api.v1 import videos, reports, growth, tasks, knowledge
from infrastructure.db.postgres import init_db, close_db
from infrastructure.db.redis import init_redis, close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # 初始化数据库
    await init_db()
    await init_redis()
    
    logger.info("Database and Redis initialized")
    
    yield
    
    # 关闭时
    logger.info("Shutting down application")
    await close_db()
    await close_redis()


# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="基于多模态AI与RAG的游戏录像智能复盘系统",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# 注册路由
app.include_router(
    videos.router,
    prefix=f"{settings.API_PREFIX}/videos",
    tags=["videos"]
)

app.include_router(
    reports.router,
    prefix=f"{settings.API_PREFIX}/reports",
    tags=["reports"]
)

app.include_router(
    growth.router,
    prefix=f"{settings.API_PREFIX}/growth",
    tags=["growth"]
)

app.include_router(
    tasks.router,
    prefix=f"{settings.API_PREFIX}/tasks",
    tags=["tasks"]
)

app.include_router(
    knowledge.router,
    prefix=f"{settings.API_PREFIX}/knowledge",
    tags=["knowledge"]
)


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
