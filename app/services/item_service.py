from app.repositories.item_repository import ItemRepository
from app.repositories.user_repository import UserRepository

# Giá cố định: (item_type, quantity) -> price
PRICE_MAP = {
    ("water_streak", 1): 200,
    ("super_xp",     1): 500,
    ("super_xp",     3): 1200,
    ("super_xp",     5): 2000,
    ("hack_xp",      1): 300,
}

# Mapping item_type -> tên cột DB
ITEM_COL_MAP = {
    "water_streak": "WaterStreak",
    "super_xp":     "SuperExperience",
    "hack_xp":      "HackExperience",
}

VALID_ITEM_TYPES = set(ITEM_COL_MAP.keys())


class ItemService:
    def __init__(self):
        self.item_repo = ItemRepository()
        self.user_repo = UserRepository()

    def _get_user_id(self, uid):
        user = self.user_repo.get_by_uid(uid)
        if not user:
            return None, "User not found"
        return user.id, None

    def get_items(self, uid):
        user_id, error = self._get_user_id(uid)
        if error:
            return None, error
        item = self.item_repo.get_or_create(user_id)
        return item, None

    def purchase(self, uid, item_type, quantity):
        if item_type not in VALID_ITEM_TYPES:
            return None, None, f"Invalid item_type. Must be one of: {', '.join(VALID_ITEM_TYPES)}"

        price = PRICE_MAP.get((item_type, quantity))
        if price is None:
            return None, None, f"Invalid quantity {quantity} for item '{item_type}'"

        user_id, error = self._get_user_id(uid)
        if error:
            return None, None, error

        item_col = ITEM_COL_MAP[item_type]
        try:
            item, diamond_remaining = self.item_repo.purchase(user_id, item_col, quantity, price)
            return item, diamond_remaining, None
        except ValueError as e:
            return None, None, str(e)

    def use_item(self, uid, item_type):
        if item_type not in VALID_ITEM_TYPES:
            return None, f"Invalid item_type. Must be one of: {', '.join(VALID_ITEM_TYPES)}"

        user_id, error = self._get_user_id(uid)
        if error:
            return None, error

        item_col = ITEM_COL_MAP[item_type]
        try:
            item = self.item_repo.use_item(user_id, item_col)
            return item, None
        except ValueError as e:
            return None, str(e)
