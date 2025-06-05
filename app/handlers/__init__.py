from aiogram import Router

from . import admin
from . import user


router = Router()

router.include_routers(admin.router, user.router)
