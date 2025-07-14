# Unified Interactible Object Design for TAG System

## Introduction and Historical Context

This document unifies and supersedes the "Realistic," "Interactible," and "Advanced" object design documents for the Text Adventure Game (TAG) system. It reflects the latest architecture and requirements for maximal realism, extensibility, and seamless integration with a Godot-based JRPG frontend. The end-goal is a fully integrated demo: running `python -m text` launches the game loop with all object, action, and block logic active.

## Design Philosophy and End-Goal

- **Maximal Realism:** Every object in the simulated house can be interacted with in contextually appropriate ways, supporting emergent gameplay and narrative depth.
- **Unified Object Model:** All objects are defined by extensible properties and affordances, with no distinction between "shown" and "hidden" objects. The `is_shown` property and the SIO/HIO distinction are removed.
- **Action System Consistency:** All action precondition logic must be implemented in the `check_precondition()` method of each `Action` subclass, especially in the `house_actions/` directory. This ensures maintainability and clarity.
- **Extensibility:** The system is designed for easy addition of new object types, properties, actions, and blocks.
- **Demo-Ready Integration:** All features must be testable in the integrated demo, with the backend entry point as `python -m text`.

## Unified Object Model

### Properties

Objects are instances of `Thing` (usually `Item`) and support the following property types:

- **Boolean:** `is_interactable`, `is_open`, `is_locked`, `is_on`, `is_clean`, `is_broken`, `is_sleepable`, `is_container`, `is_switchable`, `is_fillable`, `is_full`, `is_powered`, `is_connected`, `is_playable`, `is_wearable`, `is_read`, etc.
- **Numeric:** `cleanliness (0-100)`, `fullness (0-100)`, `temperature (°C)`, `battery_level (0-100)`, `volume (0-100)`, `brightness (0-100)`, `alarm_time (0-24)`, `cycle_time (min)`, `freshness (0-100)`, `weight (kg)`, `dosage`, `expiration_date`, `water_level`, `fuel_level`, `score`, `growth_stage`, `amount`, `charge_level`, etc.
- **Multimodal/String:** `color`, `material`, `state`, `genre`, `type`, `owner`, `location`, etc.

#### Example Object Definition

```python
# Example: Apple (consumable)
apple = things.Item(
    "apple",
    "a shiny red apple",
    "A delicious-looking apple."
)
apple.set_property("is_interactable", True)
apple.set_property("is_consumable", True)
apple.set_property("cleanliness", 100)

# Example: Refrigerator (highly interactable)
refrigerator = things.Item(
    "refrigerator",
    "a large refrigerator",
    "A fridge full of food."
)
refrigerator.set_property("is_interactable", True)
refrigerator.set_property("is_openable", True)
refrigerator.set_property("is_open", False)
refrigerator.set_property("is_container", True)
refrigerator.set_property("cleanliness", 80)
```

## Action System

### Architectural Rule: All Preconditions in `check_precondition()`

Every action must implement its precondition logic in the `check_precondition()` method of its `Action` subclass. This is mandatory for all actions, especially those in `house_actions/`. For example, a cleaning action should check both `is_cleanable` and `cleanliness < 100` in `check_precondition()`.

#### Example Action Class

```python
class CleanAction(Action):
    def check_precondition(self, actor, obj):
        if not obj.get_property("is_cleanable", False):
            return False, "You can't clean that."
        if obj.get_property("cleanliness", 100) >= 100:
            return False, "It's already clean."
        return True, None
    # ...
```

### Standard Actions and Preconditions

- **open/close:** `is_openable` must be True; for open, `is_open` must be False.
- **turn on/off:** `is_switchable` must be True; for on, `is_on` must be False.
- **clean:** `is_cleanable` must be True and `cleanliness < 100`.
- **eat/drink:** `is_consumable` must be True.
- **wear/remove:** `is_wearable` must be True.
- **fill/empty:** `is_fillable` must be True.
- **lock/unlock:** `is_lockable` must be True.
- **sit/sleep:** `is_sittable`/`is_sleepable` must be True.
- **use:** Contextual, must check relevant affordances.

All such checks must be in `check_precondition()`.

## Block System

Blocks restrict movement or interaction based on object state. Block logic should reference object properties and be implemented in custom `is_blocked()` methods.

#### Example Block Logic

- **Door Block:** Prevents movement if `is_locked` or not `is_open` or `is_broken`.
- **Power Block:** Prevents use if `is_powered` is False or `battery_level` is 0.
- **Cleanliness Block:** Prevents use if `is_clean` is False or `cleanliness < threshold`.

## Room and Object Catalog

Objects are placed in rooms according to the house layout. Each object is defined by its properties and available actions. Here is a sample catalog:

### Kitchen
- **Refrigerator:** open/close, store/retrieve, container, cleanliness
- **Oven:** open/close, turn on/off, cook, cleanliness
- **Microwave:** open/close, turn on/off, cook
- **Sink:** turn on/off, fill, clean
- **Cabinets:** open/close, container
- **Trash Can:** open/close, container
- **Toaster:** turn on/off, toast
- **Coffee Maker:** turn on/off, brew
- **Food Items:** eat, cook
- **Dishes/Utensils:** use, clean

### Bathroom
- **Toilet:** flush, open/close lid
- **Sink:** turn on/off, fill, clean
- **Bathtub:** fill/drain, enter
- **Shower:** turn on/off, enter
- **Medicine Cabinet:** open/close, container
- **Medicine:** take, use
- **Toothbrush/Toothpaste:** use

### Living Room
- **TV:** turn on/off, change channel
- **Remote Control:** use
- **Couch:** sit, search
- **Lamp:** turn on/off
- **Bookshelf:** search, get, put
- **Book:** read
- **Board Game:** play, open

### Bedroom
- **Bed:** sleep, search
- **Closet/Dresser:** open/close, container
- **Alarm Clock:** set, turn on/off
- **Clothes:** wear, remove

### Utility/Other
- **Door:** open/close, lock/unlock
- **Window:** open/close
- **Light Switch:** turn on/off
- **Thermostat:** set
- **Phone:** use, call
- **Computer:** use, turn on/off
- **Battery:** use, insert
- **Flashlight:** turn on/off, insert battery

### Outdoor
- **Mailbox:** open/close, get, put
- **Garden Hose:** turn on/off, use
- **Grill:** turn on/off, cook
- **Lawn Mower:** start/stop, use

## Integration and Testing

- **Running the Demo:** Ensure that `python -m text` launches the game loop with all objects, actions, and blocks active.
- **Testing:** All new features must be testable in the integrated demo. Edge cases (e.g., trying to clean an already clean object) must be handled gracefully by precondition checks.

## Extensibility and Future Work

- The system is designed for easy addition of new object types, properties, actions, and blocks.
- All new features should follow the architectural rules outlined here.
- Documentation and code should be updated in tandem.

## Appendix: Example Code Snippets

### Example: Action with Precondition

```python
class TurnOnAction(Action):
    def check_precondition(self, actor, obj):
        if not obj.get_property("is_switchable", False):
            return False, "You can't turn that on."
        if obj.get_property("is_on", False):
            return False, "It's already on."
        return True, None
    # ...
```

### Example: Block Logic

```python
class DoorBlock(Block):
    def is_blocked(self, obj):
        if obj.get_property("is_locked", False):
            return True
        if not obj.get_property("is_open", True):
            return True
        if obj.get_property("is_broken", False):
            return True
        return False
```

---

**This document is the canonical reference for all interactible object and action design in the TAG system. All contributors must adhere to these guidelines for future development and integration.** 