from aiogram import Router

from . import start, admin, order, add_food

router = Router()

router.include_routers(start.router, admin.router, order.router, add_food.router)
