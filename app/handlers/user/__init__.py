from aiogram import Router

from . import start, order

from .utils import foods, food_categories

router = Router()

router.include_routers(start.router, order.router)
