import aiosqlite

from app import DATABASE_URL


class Database:
    def __init__(self):
        self.conn = None

    async def connect(self) -> None:
        self.conn = await aiosqlite.connect(DATABASE_URL)
        await self.create_table()

    async def create_table(self) -> None:
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                """
                                 CREATE TABLE IF NOT EXISTS food
                                 (
                                     id          INTEGER PRIMARY KEY AUTOINCREMENT,
                                     naming      TEXT NOT NULL,
                                     description TEXT,
                                     price       INTEGER  NOT NULL,
                                     image       TEXT
                                 )
                                 """
            )
            await self.conn.commit()

    async def add_food(
        self,
        naming: str,
        price: int,
        image: str | None = None,
        description: str | None = None,
    ) -> None | int:
        try:
            async with self.conn.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO food (naming, description, price, image) VALUES (?, ?, ?, ?)",
                    (naming, description, price, image),
                )
                await self.conn.commit()
                return cursor.lastrowid
        except aiosqlite.IntegrityError:
            return None

    async def get_food(
        self, food_id: int
    ) -> tuple[str, str | None, int, str | None] | None:
        async with self.conn.cursor() as cursor:
            await cursor.execute(
                "SELECT naming, description, price, image FROM food WHERE id = ?",
                (food_id,),
            )
            return await cursor.fetchone()

    async def update_food(
        self,
        food_id: int,
        naming: str | None = None,
        price: int | None = None,
        image: str | None = None,
        description: str | None = None,
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

        if updates:
            params.append(food_id)
            query = f"UPDATE food SET {', '.join(updates)} WHERE id = ?"
            async with self.conn.cursor() as cursor:
                await cursor.execute(query, params)
                await self.conn.commit()
                return cursor.rowcount > 0
        return False

    async def delete_food(self, food_id: int) -> bool:
        async with self.conn.cursor() as cursor:
            await cursor.execute("DELETE FROM food WHERE id = ?", (food_id,))
            await self.conn.commit()
            return cursor.rowcount > 0

    async def get_all_food(self) -> list[tuple[int, str, str | None, int, str | None] | None]:
        async with self.conn.cursor() as cursor:
            await cursor.execute("SELECT * FROM food")
            return await cursor.fetchall()

    async def close(self):
        if self.conn:
            await self.conn.close()
