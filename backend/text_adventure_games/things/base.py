from collections import defaultdict


class Thing:
    """
    Supertype that will add shared functionality to Items, Locations and
    Characters.
    """

    def __init__(self, name: str, description: str):
        # A short name for the thing
        self.name = name

        # A description of the thing
        self.description = description

        # A dictionary of properties and their values. Boolean properties for
        # items include: gettable, is_wearable, is_drink, is_food, is_weapon,
        #     is_container, is_surface
        self.properties = defaultdict(bool)

        # A set of special command associated with this item. The key is the
        # command text in invoke the special command. The command should be
        # implemented in the Parser.
        self.commands = set()


    def set_property(self, property_name: str, property):
        """
        Sets the property of this item
        """
        self.properties[property_name] = property

    def get_property(self, property_name: str, default=None):
        """
        Gets the value of this property for this item (returns default if not set)
        """
        return self.properties.get(property_name, default)

    def add_command_hint(self, command: str):
        """
        Adds a special command to this thing
        """
        self.commands.add(command)

    def get_command_hints(self):
        """
        Returns a list of special commands associated with this object
        """
        return self.commands

