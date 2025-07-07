from backend.text_adventure_games.things.items import Item

class Container(Item):
    """
    A canonical container item that can hold other items, be opened/closed, and is registered for lookup.
    """
    registry = {}

    def __init__(self, name, description, is_openable=True, is_open=False, is_locked=False):
        super().__init__(name, description)
        self.set_property("is_container", True)
        self.set_property("is_openable", is_openable)
        self.set_property("is_open", is_open)
        self.set_property("is_locked", is_locked)
        self.inventory = {}
        # Register this container by name
        Container.registry[self.name] = self

    def add_item(self, item):
        self.inventory[item.name] = item
        item.location = self

    def remove_item(self, item):
        if item.name in self.inventory:
            del self.inventory[item.name]
            item.location = None

    def has_item(self, item_name):
        return item_name in self.inventory

    def list_items(self):
        return list(self.inventory.values())

    @classmethod
    def get(cls, name):
        return cls.registry.get(name)

    @classmethod
    def all(cls):
        return list(cls.registry.values()) 