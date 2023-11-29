from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi.middleware.cors import CORSMiddleware

from redis import asyncio as aioredis
from auth.base_config import fastapi_users, auth_backend
from auth.manager import get_user_manager
from auth.schemas import UserReadOld, UserCreate, UserRead, UserUpdate
from config import REDIS_HOST, REDIS_PORT
from core.initial_data import create_initial_data
from server.router import router as router_server
from tariff.router import router as router_tariff
from account.router import router as router_account
from profiles.router import router as router_profile
from profiles.dymamic import router as dynamic_router
from outline_key.router import router as router_outline_key
from admin.router import router as admin_router
from partner.router import router as partner_router
from status.router import router as status_router
from vpn_type.router import router as router_vpn_type
from referent.router import router as referent_router
from referent_type.router import router as referent_type_router
from payment.router import router as payment_router

from user.router import router as router_user, get_users_router
# from tools.router import router as router_tools
# from vless_key.router import router as router_vless_key

current_user = fastapi_users.current_user()

app = FastAPI(title="Insta VPN")

"""Мои API"""
app.include_router(payment_router)
app.include_router(router_account)
app.include_router(referent_router)
app.include_router(admin_router)
app.include_router(dynamic_router)
app.include_router(router_profile)
app.include_router(router_outline_key)
app.include_router(router_server)
app.include_router(partner_router)
app.include_router(status_router)
app.include_router(router_tariff)
app.include_router(referent_type_router)
app.include_router(router_vpn_type)

# пригодится в будущем
# app.include_router(router_outline)
# app.include_router(router_tools)
# app.include_router(router_vless_key)


app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["Bearer-auth"]
                  )

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserReadOld, UserCreate),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(
    get_users_router(user_schema=UserRead, user_update_schema=UserUpdate, get_user_manager=get_user_manager),
    prefix="/users",
    tags=["users"],
)

app.include_router(
    fastapi_users.get_verify_router(UserReadOld),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# это более безопасный подход, надо - вот так!
# origins = [
#     "http://localhost:3000",
#     "http://localhost:8000",
#     "http://90.156.229.61:8000/docs#/",
#     "http://90.156.229.61:8000/"
# ]
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
#     allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
#                    "Authorization"],
# )


@app.on_event("startup")
async def startup_event():
    redis = aioredis.from_url(f"redis://{REDIS_HOST:{REDIS_PORT}}", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    await create_initial_data()


# @app.get("/protected-route")
# def protected_route(user: User = Depends(current_user)):
#     return f"Hello, {user.email}"

"""Не удалять!!!Важно для отображения ошибок"""
from core.errors import *
