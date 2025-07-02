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

**Please review and suggest any changes or additions. Once approved, implementation will proceed.** 