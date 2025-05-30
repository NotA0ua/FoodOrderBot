from aiogram import Router

from . import start, admin

router = Router()

router.include_routers(start.router, admin.router)
