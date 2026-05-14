from aiogram import Router
from .form import router
from .admin import admin_router
# from .repair_works import router as repair_works_router

users_router = Router()

users_router.include_router(router)
users_router.include_router(admin_router)
# users_router.include_router(repair_works_router)
