from app.utils.database import get_db_connection
from app.models.item import Item


class ItemRepository:

    def get_by_user_id(self, user_id):
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM Item WHERE UserId = %s LIMIT 1", (user_id,))
                row = cursor.fetchone()
                return Item.from_dict(row) if row else None
        finally:
            connection.close()

    def get_or_create(self, user_id):
        """Return existing Item row or create a zeroed one."""
        item = self.get_by_user_id(user_id)
        if item:
            return item
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO Item (WaterStreak, SuperExperience, HackExperience, UserId) VALUES (0, 0, 0, %s)",
                    (user_id,)
                )
            connection.commit()
            return self.get_by_user_id(user_id)
        finally:
            connection.close()

    def purchase(self, user_id, item_col, quantity, price):
        """
        Atomically deduct `price` diamonds from User and add `quantity` to item_col.
        Returns (item, diamond_remaining) or raises ValueError on insufficient funds.
        """
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Lock user row
                cursor.execute("SELECT Id, Diamond FROM `User` WHERE Id = %s FOR UPDATE", (user_id,))
                user_row = cursor.fetchone()
                if not user_row:
                    raise ValueError("User not found")

                diamond = user_row.get("Diamond", 0)
                if diamond < price:
                    raise ValueError("Not enough diamonds")

                new_diamond = diamond - price
                cursor.execute("UPDATE `User` SET Diamond = %s WHERE Id = %s", (new_diamond, user_id))

                # Upsert item row
                cursor.execute("SELECT Id FROM Item WHERE UserId = %s LIMIT 1", (user_id,))
                item_row = cursor.fetchone()
                if item_row:
                    cursor.execute(
                        f"UPDATE Item SET `{item_col}` = `{item_col}` + %s WHERE UserId = %s",
                        (quantity, user_id)
                    )
                else:
                    cols = {"WaterStreak": 0, "SuperExperience": 0, "HackExperience": 0}
                    cols[item_col] = quantity
                    cursor.execute(
                        "INSERT INTO Item (WaterStreak, SuperExperience, HackExperience, UserId) VALUES (%s, %s, %s, %s)",
                        (cols["WaterStreak"], cols["SuperExperience"], cols["HackExperience"], user_id)
                    )

            connection.commit()

            item = self.get_by_user_id(user_id)
            return item, new_diamond
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def use_item(self, user_id, item_col):
        """
        Decrement item_col by 1. Raises ValueError if quantity is 0.
        Returns updated Item.
        """
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT `{item_col}` AS qty FROM Item WHERE UserId = %s LIMIT 1 FOR UPDATE",
                    (user_id,)
                )
                row = cursor.fetchone()
                if not row or row.get("qty", 0) <= 0:
                    raise ValueError("No items of this type")

                cursor.execute(
                    f"UPDATE Item SET `{item_col}` = `{item_col}` - 1 WHERE UserId = %s",
                    (user_id,)
                )
            connection.commit()
            return self.get_by_user_id(user_id)
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
