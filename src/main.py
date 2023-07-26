from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi.middleware.cors import CORSMiddleware

from redis import asyncio as aioredis
from auth.base_config import auth_backend, fastapi_users
from auth.manager import get_user_manager
from auth.models import User
from auth.schemas import UserRead, UserCreate, UserUpdate, UserReadOld
from config import REDIS_HOST, REDIS_PORT

from role.router import router as router_role
from old_code.promo.router import router as router_promo
from old_code.dish.router import router as router_dish
from old_code.selling_point.router import router as router_selling_point
from old_code.selling_point_type.router import router as router_sp_type
from old_code.order_status.router import router as router_order_status

from user.router import router as router_user, get_users_router
from core.initial_data import create_initial_data
from old_code.cart.router import router as router_cart
from old_code.order.router import router as router_order


current_user = fastapi_users.current_user()

app = FastAPI(
    title="Insta VPN"
)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["Bearer-auth"]
                  )

# app.include_router(
#     fastapi_users.get_auth_router(auth_backend),
#     prefix="/auth",
#     tags=["Auth"],
# )

app.include_router(
    fastapi_users.get_register_router(UserReadOld, UserCreate),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(router_user)
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

app.include_router(router_role)
# app.include_router(router_promo)
# app.include_router(router_dish)
# app.include_router(router_selling_point)
# app.include_router(router_sp_type)
# app.include_router(router_cart)
# app.include_router(router_order)
# app.include_router(router_order_status)

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
    # await create_initial_data()


@app.get("/protected-route")
def protected_route(user: User = Depends(current_user)):
    return f"Hello, {user.email}"
