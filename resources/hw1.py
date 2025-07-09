#!/usr/bin/env python
# coding: utf-8

# In[1]:


from text_adventure_games import (
    games, parsing, actions, things, blocks, viz
)


# In[2]:


cottage = things.Location(
    "Cottage",
    "You are standing in a small cottage."
)
garden_path = things.Location(
    "Garden Path",
    "You are standing on a lush garden path. There is a cottage here.",
)
fishing_pond = things.Location(
    "Fishing Pond",
    "You are at the edge of a small fishing pond."
)
winding_path = things.Location(
    "Winding Path",
    "You are walking along a winding path. There is a tall tree here.",
)
top_of_tree = things.Location(
    "Top of the Tall Tree",
    "You are the top of the tall tree."
)
drawbridge = things.Location(
    "Drawbridge",
    "You are standing on one side of a drawbridge leading to ACTION CASTLE.",
)
courtyard = things.Location(
    "Courtyard",
    "You are in the courtyard of ACTION CASTLE."
)
tower_stairs = things.Location(
    "Tower Stairs",
    "You are climbing the stairs to the tower. There is a locked door here.",
)
tower = things.Location(
    "Tower",
    "You are inside a tower."
)
dungeon_stairs = things.Location(
    "Dungeon Stairs",
    "You are climbing the stairs down to the dungeon."
)
dungeon = things.Location(
    "Dungeon",
    "You are in the dungeon. There is a spooky ghost here."
)
feasting_hall = things.Location(
    "Great Feasting Hall",
    "You stand inside the Great Feasting Hall."
)
throne_room = things.Location(
    "Throne Room",
    "This is the throne room of ACTION CASTLE."
)
death = things.Location(
    "The Afterlife",
    "You are dead. GAME OVER."
)
death.set_property("game_over", True)


# Map of Locations
cottage.add_connection("out", garden_path)
garden_path.add_connection("south", fishing_pond)
garden_path.add_connection("north", winding_path)
winding_path.add_connection("up", top_of_tree)
winding_path.add_connection("east", drawbridge)
top_of_tree.add_connection("jump", death)
drawbridge.add_connection("east", courtyard)
courtyard.add_connection("up", tower_stairs)
courtyard.add_connection("down", dungeon_stairs)
courtyard.add_connection("east", feasting_hall)
tower_stairs.add_connection("up", tower)
dungeon_stairs.add_connection("down", dungeon)
feasting_hall.add_connection("east", throne_room)



# In[ ]:


tempgame = games.Game(tower, things.Character(name="Temp Player", description="", persona=""))

from text_adventure_games.viz import Visualizer
viz = Visualizer(tempgame)
graph = viz.visualize()
graph


# In[4]:


# Put a fishing pole at the cottage
fishing_pole = things.Item(
    "pole",
    "a fishing pole",
    "A SIMPLE FISHING POLE.",
)
cottage.add_item(fishing_pole)


# Put a branch in a tree that could be used as a weapon
branch = things.Item(
    "branch",
    "a stout, dead branch",
    "IT LOOKS LIKE IT WOULD MAKE A GOOD CLUB.",
)
branch.set_property("is_weapon", True)
branch.set_property("is_fragile", True)
top_of_tree.add_item(branch)


# Put a candle in the feasting hall
candle = things.Item(
    "candle",
    "a strange candle",
    "THE CANDLE IS COVERED IN STARGE RUNES.",
)
candle.set_property("is_lightable", True)
candle.set_property("is_lit", False)
candle.add_command_hint("light candle")
candle.add_command_hint("read runes")
feasting_hall.add_item(candle)


# In[5]:


# Put an actual pond at the fishing location
pond = things.Item(
    "pond",
    "a small fishing pond",
    "THERE ARE FISH IN THE POND.",
)
pond.set_property("gettable", False)
pond.set_property("has_fish", True)
pond.add_command_hint("catch fish")
pond.add_command_hint("catch fish with pole")
fishing_pond.add_item(pond)


# A nice rosebush for the garden path
rosebush = things.Item(
    "rosebush",
    "a rosebush",
    "THE ROSEBUSH CONTAINS A SINGLE RED ROSE.  IT IS BEAUTIFUL.",
)
rosebush.set_property("gettable", False)
rosebush.set_property("has_rose", True)
rosebush.add_command_hint("pick rose")
garden_path.add_item(rosebush)


# Throne room wouldn't be that impressive without a throne
throne = things.Item(
    "throne",
    "An ornate golden throne."
)
throne.set_property("gettable", False)
throne.add_command_hint("sit on throne")
throne_room.add_item(throne)


# A door that leads to the tower stairs
door = things.Item(
    "door",
    "a door",
    "THE DOOR IS SECURELY LOCKED."
)
door.set_property("gettable", False)
door.set_property("is_locked", True)
door.add_command_hint("unlock door")
tower_stairs.add_item(door)


# In[6]:


# Player
player = things.Character(
    name="The player",
    description="You are a simple peasant destined for greatness.",
    persona="I am on an adventure.",
)

# Player's lamp
lamp = things.Item("lamp", "a lamp", "A LAMself.")
lamp.set_property("is_lightable", True)
lamp.set_property("is_lit", False)
lamp.add_command_hint("light lamp")
player.add_to_inventory(lamp)


# In[7]:


# A Troll at the drawbridge
troll = things.Character(
    name="troll",
    description="A mean troll",
    persona="I am hungry. The guard promised to feed me if I guard the drawbridge and keep people out of the castle.",
)
troll.set_property("is_hungry", True)
troll.set_property("character_type", "troll")
drawbridge.add_character(troll)


# A guard in the courtyard
guard = things.Character(
    name="guard",
    description="A castle guard",
    persona="I am suspicious of anyone trying to enter the castle. I will prevent keep people from entering and learning the castle's dark secrets.",
)
guard.set_property("is_conscious", True)
guard.set_property("is_suspicious", True)
guard.set_property("character_type", "human")
courtyard.add_character(guard)

# Guard has a key
key = things.Item("key", "a brass key", "THIS LOOKS USEFUL")
guard.add_to_inventory(key)

# Guard has a sword
sword = things.Item("sword", "a short sword", "A SHARP SHORT SWORD.")
sword.set_property("is_weapon", True)
guard.add_to_inventory(sword)


# A Princess in the tower
princess = things.Character(
    name="princess",
    description="A princess who is beautiful and lonely. She awaits her non-gender-stereotypical soulmate.",
    persona="I am the princess. I am grieving my father's death. I feel alone.",
)
princess.set_property("is_royal", True)
princess.set_property("emotional_state", "sad and lonely")
princess.set_property("is_married", False)
princess.set_property("character_type", "human")
tower.add_character(princess)


# A ghost in the dungeon
ghost = things.Character(
    name="ghost",
    description="A ghost with bony, claw-like fingers and who is wearing a crown.",
    persona="I was murdered by the guard. I will haunt this castle until banished. If you linger before my apparition, I will plunge my ghostly hand inside you and stop your heart",
)
ghost.set_property("character_type", "ghost")
ghost.set_property("is_dead", True)
ghost.set_property("is_banished", False)
dungeon.add_character(ghost)

# Ghost's crown
crown = things.Item("crown", "a crown", "A CROWN FIT FOR A KING.")
crown.add_command_hint("wear crown")
ghost.add_to_inventory(crown)



# In[8]:


class Unlock_Door(actions.Action):
    ACTION_NAME = "unlock door"
    ACTION_DESCRIPTION = "Unlock a door with a key"
    ACTION_ALIASES = []

    def __init__(self, game, command):
        super().__init__(game)
        # TODO - your code here
        self.character = self.parser.get_character(command)
        self.key = self.key = self.parser.match_item(
            "key", self.parser.get_items_in_scope(self.character)
        )
        self.door = self.parser.match_item(
            "door", self.parser.get_items_in_scope(self.character)
        )
        # HINT: take a look at text_adventures/actions for some examples of actions!

    def check_preconditions(self) -> bool:
        """
        Preconditions:
        * There must be a door
        * The character must be at the same location as the door
        * The door must be locked
        * The character must have the key in their inventory
        """
        # TODO - your code here
        if not self.was_matched(self.door, "There's no door here."):
            return False
        if not self.door.get_property("is_locked"):
            self.parser.fail("The door is unlocked.")
            return False
        if not self.was_matched(self.key, "The key isn't here!"):
            return False
        return True

    def apply_effects(self):
        """
        Effects:
        * Unlocks the door
        """
        # TODO - your code here
        self.door.set_property("is_locked", False)

        d = "".join(
            [
                f"{self.character.name} pulls a key out of their pocket ",
                "and - creeeeeeek - the door opens!",
            ]
        )
        description = d.format(character_name=self.character.name)
        self.parser.ok(description)


# In[9]:


class Read_Runes(actions.Action):
    """
    Reading the runes on the candle with strange runes on it will banish the
    ghost from the dungeon, and cause it to drop the crown.
    """
    ACTION_NAME = "read runes"
    ACTION_DESCRIPTION = "Read runes off of the candle"
    ACTION_ALIASES = []

    def __init__(self, game, command):
        super().__init__(game)
        # TODO - your code here
        self.character: things.Character = self.parser.get_character(command)
        self.candle: things.Item = self.parser.match_item(
            "candle", self.parser.get_items_in_scope(self.character)
        )
        self.ghost: things.Character = self.parser.get_character("ghost")


    def check_preconditions(self) -> bool:
        """
        Preconditions:
        * There must be a candle with strange runes on it
        * The character must have the candle in their inventory
        * the ghost must be in this location
        * The candle must be lit
        """
        # TODO - your code here
        if not self.candle:
            return False
        if not self.character.is_in_inventory(self.candle):
            return False
        if not self.ghost.location == self.character.location:
            self.parser.fail("There's no ghost here.")
            return False
        if not self.candle.get_property("is_lit"):
            return False
        return True

    def apply_effects(self):
        """
        Effects:
        * Banishes the ghost, causing it to drop its inventory.
        """
        # TODO - your code here
        self.ghost.set_property("is_banished", True)
        crown = self.ghost.inventory.get("crown")
        if crown:
            self.ghost.remove_from_inventory(crown)
            self.character.add_to_inventory(crown)


# In[10]:


class Propose(actions.Action):
    """
    Mawwige is whut bwings us togevveh today.
    """
    ACTION_NAME = "propose marriage"
    ACTION_DESCRIPTION = "Propose marriage to someone"
    ACTION_ALIASES = []


    def __init__(self, game, command):
        super().__init__(game)
        # TODO - your code here
        self.proposer: things.Character = self.parser.get_character(command)
        self.propositioned: things.Character = self.parser.get_character("princess")

    def check_preconditions(self) -> bool:
        """
        Preconditions:
        * The two characters must be in the same place
        * Neither can be married yet
        * Both must be happy
        """
        # TODO - your code here
        if not self.was_matched("princess", "The princess is not here."):
            return False
        if self.propositioned.get_property("is_married"):
            self.parser.fail("The princess is already married.")
            return False
        if self.proposer.get_property("is_married"):
            self.parser.fail("You are already married.")
            return False
        if not self.property_equals(
            self.propositioned,
            "emotional_state",
            "happy",
            f"{self.propositioned} is not happy!",
            True, True
        ):
            return False
        if not self.property_equals(
            self.proposer,
            "emotional_state",
            "happy",
            f"{self.proposer} is not happy!",
            True, True
        ):
            return False
        return True

    def apply_effects(self):
        """
        Effects:
        * They said "Yes!"
        * They are married.
        * If one is a royal, they are now both royals
        """
        # TODO - your code here
        self.propositioned.set_property("spouse", self.proposer)
        self.proposer.set_property("spouse", self.propositioned)

        if self.propositioned.get_property("is_royal"):
            self.proposer.set_property("is_royal", True)
        if self.proposer.get_property("is_royal"):
            self.propositioned.set_property("is_royal", True)

        description = "".join(
            [
                f"{self.proposer.name} proposes to {self.propositioned.name},"
                "and they accept! What a wonderful day! Both sides say \"Yes!\"",
            ]
        )
        self.parser.ok(description)


# In[11]:


class Wear_Crown(actions.Action):
    ACTION_NAME = "wear crown"
    ACTION_DESCRIPTION = "Put a crown in your inventory atop your head"
    ACTION_ALIASES = []

    def __init__(self, game, command):
        super().__init__(game)
        # TODO - your code here
        self.character: things.Character = self.parser.get_character(command)
        self.crown: things.Item = self.parser.match_item(
            "crown", self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        """
        Preconditions:
        * The crown must be in the character's inventory
        * The the character must be a royal
        """
        # TODO - your code here
        if not self.crown:
            return False
        if not self.character.is_in_inventory(self.crown):
            return False
        if not self.character.get_property("is_royal"):
            return False
        return True

    def apply_effects(self):
        """
        The character is crowned.
        """
        # TODO - your code here
        self.character.set_property("is_crowned", True)
        self.character.set_property("is_reigning", True)

        description = "".join(
            [
                f"{self.character.name} is crowned! All hail {self.character.name}!",
            ]
        )
        self.parser.ok(description)


# In[12]:


class Sit_On_Throne(actions.Action):
    ACTION_NAME = "sit on throne"
    ACTION_DESCRIPTION = "Sit on the throne, if you are royalty"
    ACTION_ALIASES = []

    def __init__(self, game, command):
        super().__init__(game)
        # TODO - your code here
        self.character: things.Character = self.parser.get_character(command)
        self.throne: things.Item = self.parser.match_item(
            "throne", self.parser.get_items_in_scope(self.character)
        )

    def check_preconditions(self) -> bool:
        """
        Preconditions:
        * The character must be in same location as the throne
        * The the character must be a royal
        """
        # TODO - your code here
        if not self.throne:
            return False
        if not self.character.get_property("is_royal"):
            return False
        return True

    def apply_effects(self):
        """
        The character is crowned.
        """
        # TODO - your code here
        self.character.set_property("is_crowned", True)
        self.character.set_property("is_reigning", True)

        description = "".join(
            [
                f"{self.character.name} is crowned! All hail {self.character.name}!",
            ]
        )
        self.parser.ok(description)


# In[13]:


# Sample Block

class Troll_Block(blocks.Block):
    """
    Blocks progress in this direction until the troll is no longer hungry, or
    leaves, or is unconscious, or dead.
    """

    def __init__(self, location: things.Location, troll: things.Character):
        super().__init__(
            "A troll blocks your way", "A hungry troll blocks your way"
        )
        self.location = location
        self.troll = troll

    def is_blocked(self) -> bool:
        # Conditions of block:
        # * There is a troll here
        # * The troll is alive and conscious
        # * The troll is still hungry
        if (self.troll and
            self.location.here(self.troll) and 
            not self.troll.get_property("is_dead") and
            self.troll.get_property("is_conscious") and
            self.troll.get_property("is_hungry")):
            return True
        return False


# In[ ]:


class Guard_Block(blocks.Block):
    """
    Blocks progress in this direction until the guard is no longer suspicious, or
    leaves, or is unconscious, or dead.
    """

    def __init__(self, location: things.Location, guard: things.Character):
        super().__init__(
            "A guard blocks your way", "The guard refuses to let you pass."
        )
        self.location = location
        self.guard = guard

    def is_blocked(self) -> bool:
        # Conditions of block:
        # * There is a guard here
        # * The guard is alive and conscious
        # * The guard is suspicious

        # TODO - your code here
        if (self.guard and
            self.location.here(self.guard) and
            not self.guard.get_property("is_dead") and
            self.guard.get_property("is_conscious") and
            self.guard.get_property("is_suspicious")):
                return True
        return False


# In[ ]:


class Darkness(blocks.Block):
    """
    Blocks progress in this direction unless the character has something that lights the way.
    """

    def __init__(self, location: things.Location):
        super().__init__("Darkness blocks your way", "It's too dark to go that way.")
        self.location = location

    def is_blocked(self) -> bool:
        # Conditions of block:
        # * The location is dark
        # * Unblocked if any character at the location is carrying a lit item 
        #   (like a lamp or candle)
        # TODO - your code here
        if not self.location.get_property("is_dark"):
            return False
        if any(
            item.get_property("is_lightable") and
            item.get_property("is_lit")
            for char in self.location.characters.values()
            for item in char.inventory.values()
        ):
            return False
        return True


# In[ ]:


class Door_Block(blocks.Block):
    """
    Blocks progress in this direction until the character unlocks the door.
    """

    def __init__(self, location: things.Location, door: things.Item):
        super().__init__("A locked door blocks your way", "The door ahead is locked.")
        # TODO - your code here
        self.location = location
        self.door = door

    def is_blocked(self) -> bool:
        # Conditions of block:
        # * The door is locked
        # TODO - your code here
        if self.location.here(door) and door.get_property("is_locked"):
            return True
        return False


# In[ ]:


# TODO Add blocks to location to:
# * the courtyard - the guard prevents you from going East
# * the dungeon_stairs - the darkness prevents you from going Down
# * the tower stairs - the locked door prevents you from going Up

troll_block = Troll_Block(drawbridge, troll)
drawbridge.add_block("east", troll_block)

guard_block = Guard_Block(courtyard, guard)
courtyard.add_block("east", guard_block)

darkness_block = Darkness(dungeon_stairs)
dungeon_stairs.add_block("down", darkness_block)

door_block = Door_Block(tower_stairs, door)
tower_stairs.add_block("up", door_block)


# In[ ]:


class ActionCastle(games.Game):
    def __init__(
        self, start_at: things.Location, player: things.Character, characters=None,
        custom_actions=None
    ):
        super().__init__(start_at, player, characters=characters, custom_actions=custom_actions)

    def is_won(self) -> bool:
        """ 
        Checks whether the game has been won. For Action Castle, the game is won
        once any character is sitting on the throne (has the property is_reigning).
        """
        for name, character in self.characters.items():
            if character.get_property("is_reigning"):
                msg = "{name} is now reigns in ACTION CASTLE! {name} has won the game!"
                self.parser.ok(msg.format(name=character.name.title()), self)
                return True
        return False


# In[ ]:


characters = [troll, guard, princess, ghost]
custom_actions = [Unlock_Door, Read_Runes, Propose, Wear_Crown, Sit_On_Throne]

# The Game
game = ActionCastle(cottage, player, characters=characters, custom_actions=custom_actions)


# In[ ]:


game.game_loop()

