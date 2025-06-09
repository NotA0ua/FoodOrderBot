from aiogram import Router

from . import start, food, order, cart, search

from .utils import foods, food_categories

router = Router()

router.include_routers(start.router, food.router, order.router, cart.router, search.router)
