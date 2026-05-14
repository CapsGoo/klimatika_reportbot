from aiogram import Router, types

from .cancel import router as cancel_router
from .message import router as message_router
from .form import form_router
from .admin import admin_router
# from .repair_works import router as repair_works_router

users_router = Router()

users_router.include_router(cancel_router)
users_router.include_router(message_router)
users_router.include_router(form_router)
users_router.include_router(admin_router)

# users_router.include_router(repair_works_router)
