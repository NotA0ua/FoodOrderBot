import aiosqlite

from app.env import DATABASE_URL


class Database:
    def __init__(self):
        self.conn = None

    async def connect(self) -> None:
        self.conn = await aiosqlite.connect(DATABASE_URL)
        await self.create_table()

    async def close(self):
        if self.conn:
            await self.conn.close()

    async def create_table(self) -> None:
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS foods
                (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    naming      TEXT    NOT NULL,
                    description TEXT,
                    price       INTEGER NOT NULL,
                    image       TEXT,
                    category    TEXT
                )
                """
            )

            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS orders
                (
                    id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    food_id INTEGER NOT NULL,
                    amount  INTEGER NOT NULL
                )
                """
            )

            await cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS admins
                (
                    id INTEGER PRIMARY KEY
                )
                """
            )

            await self.conn.commit()

    # ----------------------------------------

    async def add_food(
        self,
        naming: str,
        price: int,
        image: str | None = None,
        description: str | None = None,
        category: str | None = None,
    ) -> None | int:
        try:
            async with self.conn.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO foods (naming, description, price, image, category) VALUES (?, ?, ?, ?, ?)",
                    (naming, description, price, image, category),
                )
                await self.conn.commit()
                return cursor.lastrowid
        except aiosqlite.IntegrityError:
            return None

    async def get_food(
        self, food_id: int
    ) -> tuple[str, str | None, int, str | None, str | None] | None:
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT naming, description, price, image, category FROM foods WHERE id = ?",
                (food_id,),
            )
            return await cursor.fetchone()

    async def get_food_by_naming(
            self, naming: str
    ) -> list[tuple[int, str, str | None, int, str | None, str | None] | None]:
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT id, naming, description, price, image, category FROM foods WHERE naming LIKE ? COLLATE NOCASE",
                (f"%{naming}%",),
            )
            return await cursor.fetchall()

    async def update_food(
        self,
        food_id: int,
        naming: str | None = None,
        price: int | None = None,
        image: str | None = None,
        description: str | None = None,
        category: str | None = None,
    ) -> bool:
        updates = []
        params = []

        if naming:
            updates.append("naming = ?")
            params.append(naming)
        if price:
            updates.append("price = ?")
            params.append(price)
        if image:
            updates.append("image = ?")
            params.append(image)
        if description:
            updates.append("description = ?")
            params.append(description)
        if category:
            updates.append("category = ?")
            params.append(category)

        if updates:
            params.append(food_id)
            query = f"UPDATE foods SET {', '.join(updates)} WHERE id = ?"
            async with self.conn.cursor() as cursor:
                await cursor.execute(query, params)
                await self.conn.commit()
                return cursor.rowcount > 0
        return False

    async def delete_food(self, food_id: int) -> bool:
        async with self.conn.cursor() as cursor:
            await cursor.execute("DELETE FROM foods WHERE id = ?", (food_id,))
            await self.conn.commit()
            return cursor.rowcount > 0

    async def get_all_food(
        self,
    ) -> list[tuple[int, str, int] | None]:
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT id, naming, price FROM foods")
            return await cursor.fetchall()

    async def get_all_categories(self) -> list[str] | None:
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT category FROM foods ORDER BY category")
            categories = await cursor.fetchall()
            if categories:
                return list([i[0] for i in categories])

            return None

    async def get_all_food_by_category(
        self, category: str
    ) -> list[tuple[int, str, int] | None]:
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT id, naming, price FROM foods WHERE category = ?",
                (category,),
            )
            return await cursor.fetchall()

    # --------------------------------------------------------------------------

    async def add_order(self, user_id: int, food_id: int, amount: int) -> int | None:
        try:
            async with self.conn.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO orders (user_id, food_id, amount) VALUES (?, ?, ?)",
                    (user_id, food_id, amount),
                )

                await self.conn.commit()
                return cursor.lastrowid
        except aiosqlite.IntegrityError:
            return None

    async def update_order(self, order_id: int, amount: int) -> bool:
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "UPDATE orders SET amount = ? WHERE id = ?", (amount, order_id)
            )
            await self.conn.commit()
            return cursor.rowcount > 0

    async def get_order(self, user_id: int, food_id: int) -> int | None:
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT id FROM orders WHERE user_id = ? AND food_id = ?",
                (user_id, food_id),
            )
            order_id = await cursor.fetchall()
            if order_id:
                return int(order_id[0][0])
            return None

    async def get_order_by_id(self, order_id: int) -> tuple[int, int, int] | None:
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT user_id, food_id, amount FROM orders WHERE id = ?", (order_id,)
            )
            return await cursor.fetchall()

    async def get_all_orders(self, user_id: int) -> list[tuple[int, int, int] | None]:
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT id, food_id, amount FROM orders WHERE user_id = ?", (user_id,)
            )
            return await cursor.fetchall()

    async def delete_order(self, order_id: int) -> bool:
        async with self.conn.cursor() as cursor:
            await cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
            await self.conn.commit()
            return cursor.rowcount > 0


    async def delete_all_orders(self, user_id: int) -> bool:
        async with self.conn.cursor() as cursor:
            await cursor.execute("DELETE FROM orders WHERE user_id = ?", (user_id,))
            await self.conn.commit()
            return cursor.rowcount > 0

    # ------------------------

    async def add_admin(self, user_id: int) -> bool | None:
        try:
            async with self.conn.cursor() as cursor:
                await cursor.execute("INSERT INTO admins (id) VALUES (?)", (user_id,))
                await self.conn.commit()
                return cursor.lastrowid
        except aiosqlite.IntegrityError:
            return None

    async def get_all_admins(self) -> list[int] | None:
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM admins")
            admins = await cursor.fetchall()
            if admins:
                return list([i[0] for i in admins])

            return None

    async def delete_admin(self, admin_id: int) -> bool:
        async with self.conn.cursor() as cursor:
            await cursor.execute("DELETE FROM admins WHERE id = ?", (admin_id,))
            await self.conn.commit()
            return cursor.rowcount > 0

    async def is_there_admin(self, user_id: int) -> bool:
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT id FROM admins WHERE id = ?",
                (user_id,),
            )
            return (await cursor.fetchone()) is not None
