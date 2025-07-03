# Advanced Interactible Object Design Strategy for TAG and Godot JRPG Integration

## Overview

This document presents the next evolution of our interactible object system, building on the foundation of SIOs (Shown Interactible Objects) and HIOs (Hidden Interactible Objects) to deliver maximal realism and emergent gameplay. By introducing numeric and multimodal properties, as well as a suite of new actions and blocks, we enable a world where every object can be interacted with in nuanced, context-sensitive ways. This approach supports both the narrative depth of TAG and the visual, systemic clarity of our Godot JRPG.

## New Features and Design Intent

### Numeric and Multimodal Properties
- **Numeric properties** (e.g., cleanliness, temperature, fullness, battery level, volume, brightness) allow objects to exist in a spectrum of states, not just binary ones. This supports gradual change, resource management, and more realistic consequences for player actions.
- **Multimodal properties** (e.g., color, material, state, genre, type) provide richer descriptions and enable new forms of interaction, such as sorting, searching, or filtering objects by their attributes.
- **Boolean properties** remain for core affordances (e.g., is_interactable, is_open, is_locked, is_clean, is_broken, is_shown).

### Expanded Actions
- **Cleaning:** Players can now clean a wide range of objects, restoring their cleanliness or resetting their state. This supports chores, hygiene, and maintenance gameplay.
- **Power and Adjustment:** Many objects can be powered on/off, have their temperature, brightness, or volume set, or otherwise be adjusted numerically. This enables puzzles, comfort management, and dynamic feedback.
- **Contextual Interactions:** Actions are now tightly coupled to object properties, ensuring that only appropriate interactions are available and that every action has a meaningful effect on the world.

### Enhanced Blocks
- **Blocks** now respond to numeric and multimodal properties, not just booleans. For example, a door may block passage if it is locked or broken, an appliance may be unusable if not powered or if its cleanliness is too low, and a plate may not be used for eating if it is dirty.
- This system supports emergent gameplay, where the state of the world is a direct result of player choices and environmental factors.

### Impact on Gameplay and Extensibility
- **Realism:** The world feels more alive and responsive, with objects that degrade, improve, or change over time.
- **Discovery:** Players are rewarded for paying attention to object states and for experimenting with new actions.
- **Extensibility:** New properties and actions can be added with minimal friction, supporting future content and gameplay systems.

---

## Raw List of Properties, Actions, and Blocks

### Properties (by type)
- **Boolean:**
  - is_interactable, is_open, is_locked, is_on, is_clean, is_broken, is_shown, is_sleepable, is_made, is_container, is_switchable, is_fillable, is_clogged, is_full, is_powered, is_connected, is_playable, is_complete, is_lost, is_watered, has_mail, has_battery, is_charged, is_inserted, is_wearable, is_read
- **Numeric:**
  - cleanliness (0-100), fullness (0-100), temperature (°C), battery_level (0-100), volume (0-100), brightness (0-100), alarm_time (0-24), cycle_time (min), freshness (0-100), weight (kg), dosage, expiration_date (timestamp/int), water_level (0-100), fuel_level (0-100), score, growth_stage (0+), amount (0-100), charge_level (0-100)
- **Multimodal/String:**
  - color, material, state (e.g., fresh/spoiled/burnt), genre, type, owner, location

### Actions (by function)
- **Cleaning:**
  - clean bed, clean sink, clean table, clean plate, clean couch, clean garden tools, clean bathtub, clean oven, clean fridge, clean cabinets, clean trash can, clean lamp, clean bookshelf, clean game table, clean grill, clean mailbox, clean laundry basket, clean shower, clean medicine cabinet, clean toilet, clean chair, clean dining table, clean board game, clean remote control, clean computer, clean phone, clean flashlight
- **Power/Adjustment:**
  - turn on/off lamp, oven, tv, computer, microwave, toaster, coffee maker, grill, arcade machine, flashlight, washer, dryer
  - set temperature (oven, fridge, grill, thermostat)
  - adjust brightness (lamp)
  - adjust volume (tv, alarm clock)
- **Other Interactions:**
  - open, close, lock, unlock, break, repair, sit, sleep, make bed, eat, throw away, wear, remove, wash, fold, search, use, fill, drain, set alarm, adjust volume, set table, play, reset, start, stop, refuel, connect, disconnect, fix leak, check mail, charge, insert, remove, water, pick, update, reset, find, replace battery, set alarm, set genre, set color, set material

### Blocks (by logic)
- **Door Block:** Prevents movement if is_locked or not is_open or is_broken
- **Power Block:** Prevents use if is_powered is False or battery_level is 0
- **Cleanliness Block:** Prevents use if is_clean is False or cleanliness < threshold
- **Fullness Block:** Prevents adding items if fullness is at max
- **Other State Blocks:** Prevents use if is_broken, is_clogged, is_lost, etc.

---

This document should be referenced as the canonical source for all advanced interactible object logic, ensuring consistency and depth across both the TAG and Godot JRPG systems. 