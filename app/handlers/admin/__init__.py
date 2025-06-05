from aiogram import Router

from . import add_food, admin, add_admin

from app.middleware import AdminMiddleware

router = Router()
router.message.middleware(AdminMiddleware())
router.callback_query.middleware(AdminMiddleware())

router.include_routers(
    admin.router,
    add_admin.router,
    add_food.router,
)
