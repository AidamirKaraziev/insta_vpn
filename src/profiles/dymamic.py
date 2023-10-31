import re

from fastapi import APIRouter, Depends
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from core.raise_template import get_raise_new
from database import get_async_session
from profiles.crud import crud_profile
from profiles.schemas import ProfileUpdate
from static_key.crud import crud_static_key

router = APIRouter()


@router.get(path='/conf/{profile_id}',
            name='outline_connect',
            description='Подключение Outline '
            )
async def handle_payment(
        profile_id: UUID4,
        session: AsyncSession = Depends(get_async_session),
):
    profile, code, indexes = await crud_profile.get_profile_by_id(db=session, id=profile_id)
    await get_raise_new(code)
    # TODO сделать проверку если профиль не оплачен отправить в телеграм сообщение
    if not profile.static_key_id and profile.is_active:
        static_key, code, indexes = await crud_static_key.get_good_key(db=session)
        data = ProfileUpdate(static_key_id=static_key.id)
        profile, code, indexes = await crud_profile.update_profile(db=session, id=profile_id, update_data=data)

    static_key, code, indexes = await crud_static_key.get_static_key_by_id(db=session, id=profile.static_key_id)
    if not static_key.is_active:
        static_key, code, indexes = await crud_static_key.get_good_key(db=session)
        data = ProfileUpdate(static_key_id=static_key.id)
        profile, code, indexes = await crud_profile.update_profile(db=session, id=profile_id, update_data=data)
    access_url = re.findall(r'@(.*):', static_key.access_url)
    res_for_app = {
        "server": f"{access_url[0]}",
        "server_port": f"{static_key.port}",
        "password": f"{static_key.password}",
        "method": f"{static_key.method}"
    }
    return res_for_app



"""TEST dynamic key VLESS"""


@router.get(path='/test-vless/',
            name='outline_connect',
            description='Подключение Outline'
            )
async def handle_payment(
        session: AsyncSession = Depends(get_async_session),
):
    res = {
  "inbounds" : [
    {
      "listen" : "127.0.0.1",
      "port" : 1080,
      "protocol" : "socks",
      "settings" : {
        "auth" : "noauth",
        "udp" : true
      },
      "sniffing" : {
        "destOverride" : [
          "http",
          "tls",
          "quic",
          "fakedns"
        ],
        "enabled" : false,
        "routeOnly" : true
      },
      "tag" : "socks"
    }
  ],
  "outbounds" : [
    {
      "protocol" : "vless",
      "settings" : {
        "vnext" : [
          {
            "address" : "176.57.212.124",
            "port" : 443,
            "users" : [
              {
                "encryption" : "none",
                "flow" : "xtls-rprx-vision",
                "id" : "9c0b568d-446a-40c3-9514-bf6e724fec8a"
              }
            ]
          }
        ]
      },
      "streamSettings" : {
        "network" : "tcp",
        "realitySettings" : {
          "fingerprint" : "firefox",
          "publicKey" : "n65lCyTgyOPYaRegNqxyfZfhBaGoP7JgLkXXQBnNvSw",
          "serverName" : "yahoo.com",
          "shortId" : "f8d8328e",
          "spiderX" : "\/"
        },
        "security" : "reality",
        "tcpSettings" : {

        }
      },
      "tag" : "proxy"
    },
    {
      "protocol" : "freedom",
      "tag" : "direct"
    },
    {
      "protocol" : "blackhole",
      "tag" : "block"
    }
  ]
}

    return res
