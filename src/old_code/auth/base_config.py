from fastapi_users import FastAPIUsers

from old_code.auth.manager import get_user_manager
from old_code.auth.models import User
from config import SECRET_AUTH
from fastapi_users.authentication import (AuthenticationBackend, BearerTransport, JWTStrategy)

# cookie_transport = CookieTransport(cookie_name="neo-circassian", cookie_max_age=3600, cookie_httponly=False,
#                                    cookie_samesite="none")
#
#
# def get_jwt_strategy() -> JWTStrategy:
#     return JWTStrategy(secret=SECRET_AUTH, lifetime_seconds=3600)
#
#
# auth_backend = AuthenticationBackend(
#     name="jwt",
#     transport=cookie_transport,
#     get_strategy=get_jwt_strategy,
# )
#
# fastapi_users = FastAPIUsers[User, int](
#     get_user_manager,
#     [auth_backend],
# )
#
# current_user = fastapi_users.current_user()

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET_AUTH, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])

current_user = fastapi_users.current_user()
