# o
from backend.objects.interactive_object import Door, Container, Appliance, SteamObject

object_registry = {}

# Add front door and bathroom door
object_registry["front_door"] = Door("front_door", state="closed", location="entryway")
object_registry["bathroom_door"] = Door("bathroom_door", state="open", location="bathroom")

# Fridge in kitchen
object_registry["fridge"] = Container("fridge", state="closed", location="kitchen")

# Sink and bathtub in bathroom
object_registry["bathroom_sink"] = Appliance("bathroom_sink", state="off", location="bathroom")
object_registry["bathtub"] = Appliance("bathtub", state="off", location="bathroom")

# Coffee cup (with steam) in kitchen
object_registry["coffee_cup"] = SteamObject("coffee_cup", state="still", location="kitchen")

# Cabinet in bathroom
object_registry["bathroom_cabinet"] = Container("bathroom_cabinet", state="closed", location="bathroom")

def initialize_objects():
    """
    Optionally used to reset/re-send object state, or to show all available objects to frontend.
    (No need to call to populate `object_registry`.)
    """
    # If you want, you can refresh/repopulate here, but usually just:
    return [obj.to_dict() for obj in object_registry.values()]
