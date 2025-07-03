# Realistic Object Interactivity and Consumability in TAG

## Overview

This document outlines the planned expansion and refactor of the object, action, and block systems in the text adventure game framework to support:

- **Maximal realism** in a simulated house environment.
- **Explicit and extensible object properties** (`is_interactable`, `is_consumable`, etc.).
- **Highly Interactable Objects (HIOs)** with rich, multi-faceted behaviors.
- **New and extended actions and blocks** to support realistic interactions and environmental constraints.

---

## 1. Object Model Enhancements

### 1.1. Properties

All objects (instances of `Thing` and its subclasses) will support the following new or standardized properties:

- `is_interactable`: Boolean. True if the object can be interacted with in a meaningful way (beyond being described).
- `is_consumable`: Boolean. True if the object can be consumed, used up, or depleted (food, drink, medicine, batteries, etc.).
- Additional properties as needed for realism, e.g.:
  - `is_openable`, `is_open`
  - `is_switchable`, `is_on`
  - `is_wearable`, `is_worn`
  - `is_container`, `is_locked`
  - `is_fragile`, `is_full`, `is_dirty`, etc.

### 1.2. Highly Interactable Objects (HIOs)

HIOs are objects that:

- Can be manipulated in multiple ways (opened, closed, turned on/off, filled, emptied, etc.).
- Often have state and/or contain other objects.
- May be containers, tools, appliances, or complex furniture.

#### Example HIOs by Room

**Kitchen**
- Refrigerator (open/close, store/retrieve, is_interactable)
- Oven (turn on/off, open/close, cook, is_interactable)
- Microwave, Sink, Cabinets, Trash can, Toaster, Coffee maker, Food items, Dishes, Utensils

**Bathroom**
- Toilet (flush, open/close lid, is_interactable)
- Sink, Bathtub, Shower, Medicine cabinet, Medicine, Toothbrush, Toothpaste

**Living Room**
- TV, Remote control, Couch, Lamp, Bookshelf, Book, Board game

**Bedroom**
- Bed, Closet, Dresser, Alarm clock, Clothes

**Utility/Other**
- Door, Window, Light switch, Thermostat, Phone, Computer, Battery, Flashlight

**Outdoor**
- Mailbox, Garden hose, Grill, Lawn mower

---

## 2. Action System Enhancements

### 2.1. New/Extended Actions

Actions will be added or extended to support realistic interactions with HIOs and consumables, including but not limited to:

- `open`, `close`
- `turn on`, `turn off`
- `use`
- `eat`, `drink`
- `wear`, `remove`
- `fill`, `empty`
- `lock`, `unlock`
- `flush`, `sit`, `sleep`, `read`, `play`, etc.

Each action will:
- Check relevant preconditions (e.g., is the object present, is it interactable, is it in the right state).
- Apply effects (e.g., change state, move objects, consume items, print feedback).

### 2.2. Action Routing

The parser will be updated to recognize new actions and route commands accordingly, leveraging the flexible action registration system in TAG.

---

## 3. Block System Enhancements

### 3.1. New/Extended Blocks

Blocks will be added or extended to model realistic environmental constraints, such as:

- Locked doors (require key or code)
- Powered-off appliances (require power to operate)
- Darkness (require light source)
- NPCs blocking passage (require distraction, persuasion, etc.)
- Physical obstacles (require moving, breaking, or bypassing)

Each block will:
- Implement custom `is_blocked()` logic based on the state of relevant objects or characters.
- Provide descriptive feedback to the player.

---

## 4. Integration Plan

### 4.1. Object Placement

- Place new HIOs and consumables in appropriate rooms.
- Set initial properties and states for each object.

### 4.2. Action and Block Registration

- Register new actions and blocks with the parser and game engine.
- Ensure all interactions are discoverable and testable.

### 4.3. Testing

- Test all new objects, actions, and blocks for correct behavior and feedback.
- Ensure edge cases (e.g., trying to eat a non-consumable, open a non-openable) are handled gracefully.

---

## 5. Example Object Definition

```python
# Example: Apple (consumable)
apple = things.Item(
    "apple",
    "a shiny red apple",
    "A delicious-looking apple.",
)
apple.set_property("is_interactable", True)
apple.set_property("is_consumable", True)

# Example: Refrigerator (HIO)
refrigerator = things.Item(
    "refrigerator",
    "a large refrigerator",
    "A fridge full of food.",
)
refrigerator.set_property("is_interactable", True)
refrigerator.set_property("is_openable", True)
refrigerator.set_property("is_open", False)
refrigerator.set_property("is_container", True)
```

---

## 6. Extensibility

- The system is designed for easy addition of new object types, properties, actions, and blocks.
- All new features will be documented and follow the existing TAG architecture for maintainability.

---

## 7. Timeline and Milestones

1. **Design Review** (You!): Approve or suggest changes to this document.
2. **Object/Room Expansion**: Add new HIOs and consumables to the world.
3. **Action/Block Implementation**: Add/extend actions and blocks for realism.
4. **Integration and Testing**: Place objects, register actions/blocks, test.
5. **Documentation Update**: Update code and user documentation.

---

## 8. Detailed Object Catalog and Commentary

This section catalogs every new Highly Interactable Object (HIO) and all discussed objects, providing their function, role, and integration into the TAG module and backend server. Objects are grouped by room/area for clarity.

### 8.1. Kitchen

| Object         | Function | Role | Integration |
|---------------|----------|------|-------------|
| **Refrigerator** | Stores perishable food; can be opened/closed, used as a container | Central food storage, enables food retrieval, spoilage mechanics | `is_interactable`, `is_openable`, `is_open`, `is_container`; actions: open, close, put, get |
| **Oven**         | Cooks food; can be turned on/off, opened/closed | Enables cooking gameplay, recipes, hazards | `is_interactable`, `is_openable`, `is_open`, `is_switchable`, `is_on`; actions: open, close, turn on, turn off, cook |
| **Microwave**    | Heats food quickly | Alternative cooking, time-based puzzles | `is_interactable`, `is_openable`, `is_open`, `is_switchable`, `is_on`; actions: open, close, turn on, turn off, cook |
| **Sink**         | Provides water, can be filled/drained | Cleaning, water source, hygiene | `is_interactable`, `is_switchable`, `is_on`; actions: turn on, turn off, fill, clean |
| **Cabinets**     | Store kitchen items, can be opened/closed | Storage, hiding objects, searching | `is_interactable`, `is_openable`, `is_open`, `is_container`; actions: open, close, put, get |
| **Trash can**    | Holds waste, can be opened/closed | Waste management, searching for clues | `is_interactable`, `is_openable`, `is_open`, `is_container`; actions: open, close, put, get |
| **Toaster**      | Toasts bread, can be turned on/off | Breakfast gameplay, hazards | `is_interactable`, `is_switchable`, `is_on`; actions: turn on, turn off, toast |
| **Coffee maker** | Brews coffee, can be turned on/off | Energy mechanic, time-based events | `is_interactable`, `is_switchable`, `is_on`; actions: turn on, turn off, brew |
| **Food items**   | Can be eaten, sometimes cooked | Health, hunger, quest items | `is_interactable`, `is_consumable`, `is_food`; actions: eat, cook |
| **Dishes/Utensils** | Used for eating, can be cleaned | Realism, cleaning tasks, puzzles | `is_interactable`; actions: use, clean |

### 8.2. Bathroom

| Object         | Function | Role | Integration |
|---------------|----------|------|-------------|
| **Toilet**        | Can be flushed, lid opened/closed | Hygiene, humor, puzzle elements | `is_interactable`, `is_openable`, `is_open`; actions: flush, open, close |
| **Sink**          | Provides water, can be turned on/off | Hygiene, cleaning, water source | `is_interactable`, `is_switchable`, `is_on`; actions: turn on, turn off, fill, clean |
| **Bathtub**       | Can be filled/drained, entered | Bathing, hiding, puzzles | `is_interactable`, `is_fillable`, `is_full`; actions: fill, drain, enter |
| **Shower**        | Can be turned on/off, entered | Bathing, time-based events | `is_interactable`, `is_switchable`, `is_on`; actions: turn on, turn off, enter |
| **Medicine cabinet** | Stores medicine, can be opened/closed | Storage, health, puzzles | `is_interactable`, `is_openable`, `is_open`, `is_container`; actions: open, close, put, get |
| **Medicine**      | Can be consumed for health | Health, quest item | `is_interactable`, `is_consumable`; actions: take, use |
| **Toothbrush/Toothpaste** | Used for hygiene | Realism, daily routine, puzzles | `is_interactable`, `is_consumable` (toothpaste); actions: use |

### 8.3. Living Room

| Object         | Function | Role | Integration |
|---------------|----------|------|-------------|
| **TV**            | Can be turned on/off, channel changed | Entertainment, clues, time events | `is_interactable`, `is_switchable`, `is_on`; actions: turn on, turn off, change channel |
| **Remote control**| Controls TV, can be lost/found | Puzzle, convenience | `is_interactable`; actions: use |
| **Couch**         | Can be sat on, searched | Rest, hiding items | `is_interactable`; actions: sit, search |
| **Lamp**          | Can be turned on/off | Lighting, mood, puzzles | `is_interactable`, `is_switchable`, `is_on`; actions: turn on, turn off |
| **Bookshelf**     | Stores books, can be searched | Clues, puzzles, storage | `is_interactable`, `is_container`; actions: search, get, put |
| **Book**          | Can be read, sometimes a clue | Lore, puzzles | `is_interactable`; actions: read |
| **Board game**    | Can be played, contains pieces | Entertainment, group events | `is_interactable`, `is_container`; actions: play, open |

### 8.4. Bedroom

| Object         | Function | Role | Integration |
|---------------|----------|------|-------------|
| **Bed**           | Can be slept in, searched | Rest, time passage, hiding items | `is_interactable`; actions: sleep, search |
| **Closet**        | Stores clothes, can be opened/closed | Storage, hiding, puzzles | `is_interactable`, `is_openable`, `is_open`, `is_container`; actions: open, close, put, get |
| **Dresser**       | Stores clothes, can be opened/closed | Storage, hiding, puzzles | `is_interactable`, `is_openable`, `is_open`, `is_container`; actions: open, close, put, get |
| **Alarm clock**   | Can be set, turned on/off | Time-based events, puzzles | `is_interactable`, `is_switchable`, `is_on`; actions: set, turn on, turn off |
| **Clothes**       | Can be worn, removed | Disguise, warmth, quests | `is_interactable`, `is_wearable`, `is_worn`; actions: wear, remove |

### 8.5. Utility/Other

| Object         | Function | Role | Integration |
|---------------|----------|------|-------------|
| **Door**          | Can be opened/closed, locked/unlocked | Access control, puzzles | `is_interactable`, `is_openable`, `is_open`, `is_locked`; actions: open, close, lock, unlock |
| **Window**        | Can be opened/closed | Access, escape, puzzles | `is_interactable`, `is_openable`, `is_open`; actions: open, close |
| **Light switch**  | Controls lights | Lighting, puzzles | `is_interactable`, `is_switchable`, `is_on`; actions: turn on, turn off |
| **Thermostat**    | Sets temperature | Comfort, puzzles | `is_interactable`; actions: set |
| **Phone**         | Can be used to call | Communication, puzzles | `is_interactable`; actions: use, call |
| **Computer**      | Can be used, turned on/off | Information, puzzles | `is_interactable`, `is_switchable`, `is_on`; actions: use, turn on, turn off |
| **Battery**       | Powers devices, can be depleted | Resource management | `is_interactable`, `is_consumable`; actions: use, insert |
| **Flashlight**    | Provides portable light, can be turned on/off | Exploration, darkness puzzles | `is_interactable`, `is_switchable`, `is_on`, `is_consumable` (battery); actions: turn on, turn off, insert battery |

### 8.6. Outdoor

| Object         | Function | Role | Integration |
|---------------|----------|------|-------------|
| **Mailbox**        | Stores mail, can be opened/closed | Clues, quest items | `is_interactable`, `is_openable`, `is_open`, `is_container`; actions: open, close, get, put |
| **Garden hose**    | Waters plants, can be turned on/off | Gardening, puzzles | `is_interactable`, `is_switchable`, `is_on`; actions: turn on, turn off, use |
| **Grill**          | Cooks food, can be turned on/off | Outdoor cooking, events | `is_interactable`, `is_switchable`, `is_on`; actions: turn on, turn off, cook |
| **Lawn mower**     | Cuts grass, can be started/stopped | Chores, puzzles | `is_interactable`, `is_switchable`, `is_on`; actions: start, stop, use |

---

### Commentary on Function, Role, and Integration

- **Function**: Describes what the object does in the game world (e.g., can be opened, used, consumed, etc.).
- **Role**: Explains why the object exists from a gameplay or narrative perspective (e.g., enables puzzles, provides resources, supports realism).
- **Integration**: Details how the object is represented in the TAG module and backend server, including which properties, actions, and blocks are relevant. For HIOs, this often means multiple properties and supported actions, as well as possible custom blocks (e.g., locked doors, powered-off appliances).

All objects are implemented as subclasses of `Thing` (usually `Item`), with properties set via `set_property`. Actions are registered with the parser and can be extended for custom logic. Blocks are used to restrict movement or interaction based on object state (e.g., a locked door block).

This catalog should be updated as new objects or interactions are added to the game world.

---

**Please review and suggest any changes or additions. Once approved, implementation will proceed.**

---

## 9. Managerial Overview: Highly Interactable Objects (HIOs) and Key Objects by Room

This section provides a comprehensive, narrative overview of all Highly Interactable Objects (HIOs) and other significant objects included in the game environment. Each object is described in terms of its function, its role in gameplay or narrative, and its integration into the TAG system. This overview is intended for managerial and design stakeholders to understand the scope and purpose of each object, without technical implementation details.

### 9.1. Kitchen

- **Refrigerator**: A central storage appliance for perishable food and drinks. Players can open and close the refrigerator, store and retrieve items, and use it to prevent food spoilage. It supports a variety of interactions, making it a core HIO for resource management and realism.
- **Oven**: Used for cooking food, the oven can be turned on or off and opened or closed. It enables cooking-based puzzles and time-based events, and can introduce hazards if misused. Its stateful nature (on/off, open/closed) makes it a key HIO.
- **Microwave**: Provides a quick way to heat food. Like the oven, it can be opened, closed, turned on, and turned off, supporting alternative cooking mechanics and time-based challenges.
- **Sink**: Supplies water for cleaning and filling containers. The sink can be turned on or off, and is essential for hygiene-related tasks and certain puzzles.
- **Cabinets**: Storage spaces for dishes, utensils, and food. Cabinets can be opened and closed, and items can be placed inside or retrieved, supporting search and organization gameplay.
- **Trash Can**: Used for waste disposal, the trash can can be opened and closed. It may contain clues or items, and supports environmental management mechanics.
- **Toaster**: Allows players to toast bread, introducing breakfast routines and potential hazards. The toaster can be turned on or off and used with bread items.
- **Coffee Maker**: Enables brewing coffee, which can affect player energy or trigger events. The coffee maker can be turned on or off and used to create consumable items.
- **Food Items (Bread, Apple, Milk, etc.)**: Consumable resources that restore health or fulfill quests. These items can be eaten or drunk, and may be used in cooking or combined with other objects.
- **Dishes (Plate, Cup, Bowl)**: Used for serving and eating food. Dishes can be cleaned, used, or stored, supporting realism and certain cleaning or serving tasks.
- **Utensils (Fork, Knife, Spoon)**: Tools for eating or food preparation. Utensils can be used, cleaned, or stored, and may be required for specific actions or puzzles.

### 9.2. Bathroom

- **Toilet**: A hygiene fixture that can be flushed and have its lid opened or closed. The toilet supports realism, humor, and may be involved in puzzles or hiding items.
- **Sink**: Provides water for washing and filling containers. The bathroom sink is essential for hygiene and may be used in cleaning or health-related tasks.
- **Bathtub**: Can be filled or drained and entered by the player. The bathtub supports bathing, hiding, and certain puzzle mechanics.
- **Shower**: Used for bathing, the shower can be turned on or off and entered. It may be involved in time-based events or hygiene routines.
- **Medicine Cabinet**: A storage space for medicine and hygiene products. The cabinet can be opened or closed, and items can be retrieved or stored, supporting health and puzzle mechanics.
- **Medicine**: Consumable items that restore health or fulfill quest requirements. Medicine can be used or given to other characters.
- **Toothbrush and Toothpaste**: Hygiene items that can be used and, in the case of toothpaste, consumed. They support daily routine realism and may be involved in specific tasks or puzzles.

### 9.3. Living Room

- **TV**: An entertainment device that can be turned on or off and have its channel changed. The TV can provide clues, trigger events, or serve as a distraction, supporting both narrative and puzzle elements.
- **Remote Control**: Used to operate the TV, the remote can be found, lost, or used, supporting search and convenience mechanics.
- **Couch**: A piece of furniture that can be sat on or searched for hidden items. The couch supports rest mechanics and item discovery.
- **Lamp**: Provides lighting and can be turned on or off. The lamp is essential for visibility and may be involved in mood or puzzle mechanics.
- **Bookshelf**: Stores books and can be searched for items or clues. The bookshelf supports lore discovery and puzzle-solving.
- **Book**: Can be read for information, clues, or story progression. Books may be required for certain puzzles or quests.
- **Board Game**: An entertainment item that can be played, sometimes containing pieces or clues. Board games support group events and narrative depth.

### 9.4. Bedroom

- **Bed**: Used for sleeping, resting, or searching for hidden items. The bed supports time passage, health restoration, and item discovery.
- **Closet**: Storage for clothes and other items. The closet can be opened or closed, and supports hiding, searching, and organization gameplay.
- **Dresser**: Another storage option for clothes and personal items. Like the closet, it can be opened or closed and supports similar mechanics.
- **Alarm Clock**: Can be set and turned on or off. The alarm clock is used for time-based events, waking the player, or triggering puzzles.
- **Clothes**: Wearable items that can be put on or removed. Clothes may affect player status, disguise, or be required for certain actions or quests.

### 9.5. Utility/Other

- **Door**: Provides access between rooms and can be opened, closed, locked, or unlocked. Doors are central to navigation, access control, and puzzle mechanics, often involving keys or codes.
- **Window**: Can be opened or closed, providing alternative access, escape routes, or ventilation. Windows may be involved in puzzles or environmental effects.
- **Light Switch**: Controls lighting in a room. Light switches can be turned on or off, affecting visibility and enabling or disabling certain actions.
- **Thermostat**: Allows the player to set the room temperature. The thermostat can affect comfort, trigger events, or be part of environmental puzzles.
- **Phone**: Used to make calls, the phone can be involved in communication-based puzzles, receiving clues, or triggering events.
- **Computer**: A device that can be used and turned on or off. Computers may provide information, access to other systems, or be central to certain puzzles.
- **Battery**: A consumable resource used to power devices. Batteries can be inserted into objects like flashlights, supporting resource management mechanics.
- **Flashlight**: Provides portable light and can be turned on or off. The flashlight is essential for exploring dark areas and may require batteries to function.

### 9.6. Outdoor

- **Mailbox**: A container for mail that can be opened or closed. The mailbox may contain quest items, clues, or be involved in delivery-based puzzles.
- **Garden Hose**: Used for watering plants, the hose can be turned on or off and may be involved in gardening tasks or environmental puzzles.
- **Grill**: An outdoor cooking appliance that can be turned on or off. The grill supports cooking events, social gatherings, or specific quests.
- **Lawn Mower**: Used for cutting grass, the lawn mower can be started or stopped and may be involved in chores, maintenance, or unique puzzles.

---

**Integration into the TAG System:**

All objects and HIOs are modeled as instances of the `Thing` class (typically as `Item`), with properties such as `is_interactable`, `is_consumable`, `is_openable`, `is_switchable`, and others as appropriate. Actions (e.g., open, close, use, eat, wear) are registered in the TAG parser and are available based on the object's properties. Blocks are used to restrict movement or interaction when certain conditions are not met (e.g., a locked door or a powered-off appliance). This design ensures that every object supports meaningful, context-sensitive interactions, contributing to both gameplay depth and narrative immersion.

This catalog is exhaustive for the current design and should be updated as new objects or interactions are added to the game world.

---