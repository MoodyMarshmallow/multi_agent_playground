"""
State description utilities for the game.
"""


class DescriptionManager:
    """
    Manages description generation for game states and locations.
    """
    
    def __init__(self, game):
        self.game = game
    
    def describe_current_location(self) -> str:
        """
        Describe the current location by printing its description field.
        """
        if self.game.player.location is not None:
            return self.game.player.location.description
        else:
            raise ValueError(f"Player {self.game.player.name} location is None.")

    def describe_exits(self) -> str:
        """
        List the directions that the player can take to exit from the current location.
        """
        if self.game.player.location is not None:
            exits = []
            for direction in self.game.player.location.connections.keys():
                location = self.game.player.location.connections[direction]
                exits.append(direction.capitalize() + " to " + location.name)
            description = ""
            if len(exits) > 0:
                description = "Exits:\n"
                for exit in exits:
                    description += exit + "\n"
            return description
        else:
            raise ValueError(f"Player {self.game.player.name} location is None.")

    def describe_items(self) -> str:
        """
        Describe what items are in the current location.
        """
        if self.game.player.location is not None:
            description = ""
            if len(self.game.player.location.items) > 0:
                description = "You see:"
                for item_name in self.game.player.location.items:
                    item = self.game.player.location.items[item_name]
                    description += "\n * " + item.description
                    if self.game.give_hints:
                        description += "\n   You can:"
                        special_commands = item.get_command_hints()
                        for cmd in special_commands:
                            description += "\n\t" + cmd
            return description
        else:
            raise ValueError(f"Player {self.game.player.name} location is None.")

    def describe_characters(self) -> str:
        """
        Describe what characters are in the current location.
        """
        if self.game.player.location is not None:
            description = ""
            if len(self.game.player.location.characters) > 1:
                description = "Characters:"
                for character_name in self.game.player.location.characters:
                    if character_name == self.game.player.name:
                        continue
                    character = self.game.player.location.characters[character_name]
                    description += "\n * " + character.description
            return description
        else:
            raise ValueError(f"Player {self.game.player.name} location is None.")
    
    def describe_full_location(self) -> str:
        """
        Describe the complete current game state including location, exits, items, and characters.
        """
        description = self.describe_current_location() + "\n"
        description += self.describe_exits() + "\n"
        description += self.describe_items() + "\n"
        description += self.describe_characters() + "\n"
        return description