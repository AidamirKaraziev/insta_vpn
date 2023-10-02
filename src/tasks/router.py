from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_async_session
from tasks.tasks import deactivate_servers


router = APIRouter(prefix="/report")


# TODO возможно они должны быть синхронными
@router.get("/check-servers")
async def check_servers(session: AsyncSession = Depends(get_async_session)):
    # background_tasks
    # background_tasks.add_task(deactivate_servers, session)

    # это работает, но это не селери и не background_tasks
    objs, code, indexes = await deactivate_servers(db=session)
    return {
        "status": 200,
        "data": f"so good: ",
        "details": None
    }


# @router.get("/dashboard")
# def get_dashboard_report(user=Depends(current_user)):
#     send_email_report_dashboard.delay(user.username)
#
#     return {
#         "order_status": 200,
#         "data": "Письмо отправлено",
#         "details": None
#     }
# @router.get("/dashboard")
# def get_dashboard_report(background_tasks: BackgroundTasks, user=Depends(current_user)):
#     # 1400 ms - Клиент ждет
#     send_email_report_dashboard(user.username)
#     # 500 ms - Задача выполняется на фоне FastAPI в event loop'е или в другом треде
#     background_tasks.add_task(send_email_report_dashboard, user.username)
#     # 600 ms - Задача выполняется воркером Celery в отдельном процессе
#     send_email_report_dashboard.delay(user.username)
#     return {
#         "order_status": 200,
#         "data": "Письмо отправлено",
#         "details": None
#     }
