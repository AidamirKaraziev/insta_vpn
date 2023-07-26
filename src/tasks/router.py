from fastapi import APIRouter, BackgroundTasks, Depends


router = APIRouter(prefix="/report")

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
