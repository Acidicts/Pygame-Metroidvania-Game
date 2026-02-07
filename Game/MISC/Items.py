import json
from Game.MISC.Item import Item

class ItemManager:
    def __init__(self, game):
        self.game = game
        self.items_dict = {}
        self.items = {}
        self.data = {}

        self.load()
        self.load_items()

    def __getitem__(self, item_id):
        return self.get_item(item_id)

    def load(self):
        with open("Game/assets/data.json", "r") as f:
            self.data = json.load(f)["items"]

    def load_items(self):
        for item_id, data in self.data.items():
            self.items_dict[item_id] = data

            item = Item(self, item_id)
            self.items[item_id] = item

    def get_item(self, item_id):
        return self.items.get(item_id)