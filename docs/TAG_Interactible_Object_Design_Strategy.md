# Interactible Object Design Strategy for TAG and Godot JRPG Integration

![House Layout with Room Boundaries and Coordinates](./house_layout_grid.png)
*Figure 1: House layout with room boundaries and coordinate mapping for object placement.*

![Godot JRPG House Visual](./godot_jrpg_house.png)
*Figure 2: In-game visual representation of the house in the Godot JRPG engine.*

## Introduction

This document articulates the guiding strategy for interactible object design as we bridge the Text Adventure Game (TAG) system with a Godot-based JRPG experience. Our approach is rooted in maximal realism, player immersion, and a seamless translation between narrative-driven and visually rich gameplay. The following strategy ensures that every interactible object—whether immediately visible or discoverable through exploration—serves a clear purpose in both the story and the player's journey.

## Design Philosophy

Our design is built on the principle that a believable, engaging environment is one where every object can matter. By distinguishing between Shown Interactible Objects (SIOs) and Hidden Interactible Objects (HIOs), we create a layered world: SIOs anchor the player's expectations and guide core interactions, while HIOs reward curiosity and deepen replayability. This duality supports both the explicit, visual logic of a JRPG and the emergent, text-based exploration of TAG.

The `is_shown` parameter, implemented at the code level, is a simple but powerful tool for maintaining this distinction. It allows us to control which objects are visually highlighted in the Godot game, without constraining the narrative or the AI's understanding in TAG. This flexibility is key to supporting both systems with a single, unified object model.

## Object Properties, Actions, and Blocks

The foundation of our interactible object system is the flexible use of Thing properties, actions, and blocks. Every SIO and HIO is defined by a set of properties—such as `is_interactable`, `is_consumable`, `is_openable`, `is_shown`, and others—that determine how it can be engaged with in both the TAG and Godot environments. These properties are the backbone of our object logic, enabling a wide range of interactions and states.

Actions are mapped directly to these properties. For example, an object with `is_openable` can be opened or closed; one with `is_consumable` can be eaten, drunk, or used up; and `is_switchable` enables turning on or off. The action system ensures that only contextually appropriate interactions are available to the player, maintaining immersion and logical consistency.

Blocks are used to restrict or enable movement and interaction based on object state. Classic examples include a locked door (which blocks passage until unlocked), a powered-off appliance (which cannot be used until turned on), or a dark room (which requires a light source to enter). These blocks are tightly integrated with Thing properties and actions, providing dynamic, state-driven gameplay.

This architecture applies equally to SIOs and HIOs. Whether an object is visually prominent or hidden, its properties, available actions, and any associated blocks define its role in the world and the player's possible interactions. This unified approach supports both the narrative depth of TAG and the interactive clarity of Godot, ensuring a seamless and engaging experience across both platforms.

## SIOs vs. HIOs: Strategic Distinction

- **Shown Interactible Objects (SIOs):**
  - Visually represented and interactible in the Godot JRPG (e.g., highlighted in Figure 1).
  - Central to the player's core gameplay loop—doors, major appliances, key furniture.
  - In TAG, SIOs are described and interactible, but their visual prominence is especially important for the Godot game.

- **Hidden Interactible Objects (HIOs):**
  - Not visually highlighted in the Godot map, but present and interactible in TAG.
  - Include items that can be discovered, collected, or interacted with through exploration—utensils, books, consumables, etc.
  - HIOs add depth, discovery, and replayability, rewarding attentive and curious players.

- **Parameter for Integration:**
  - The `is_shown` parameter distinguishes SIOs (`is_shown=True`) from HIOs (`is_shown=False`).
  - This distinction is invisible to players and AI agents in TAG narration, but is essential for Godot's visual and interaction logic.

## Reference: Room Layout and Object Placement

The following lists are based on our house layout (see Figure 1) and the exhaustive object catalog developed in our design sessions. Each room's objects are categorized as SIOs or HIOs, with a brief description of their function and role.

---

## Room-by-Room Object Strategy

### Bedroom

**SIOs:**
- **Bed:** Central to rest and time passage; allows the player to sleep and recover.
- **Closet:** Main storage for clothes and personal items; can be opened and searched.
- **Dresser:** Additional storage; supports organization and item discovery.

**HIOs:**
- **Alarm Clock:** Enables time-based events and puzzles; can be set or turned off.
- **Clothes:** Wearable items for disguise, warmth, or quest requirements.

### Kitchen

**SIOs:**
- **Refrigerator:** Stores perishable food; can be opened, closed, and used for food management.
- **Oven:** Used for cooking; can be turned on/off and opened/closed.
- **Sink:** Provides water for cleaning and filling containers.
- **Cabinets:** Storage for dishes, utensils, and food; can be opened and searched.
- **Trash Can:** Waste disposal; can be opened and may contain clues.

**HIOs:**
- **Microwave:** Heats food quickly; supports alternative cooking mechanics.
- **Toaster:** Toasts bread; introduces breakfast routines and hazards.
- **Coffee Maker:** Brews coffee; affects player energy and triggers events.
- **Food Items (Bread, Apple, Milk, etc.):** Consumables for health, hunger, or quests.
- **Dishes (Plate, Cup, Bowl):** Used for serving and eating food; can be cleaned or stored.
- **Utensils (Fork, Knife, Spoon):** Tools for eating or food preparation; may be required for specific actions.

### Entry Room

**SIOs:**
- **Entry Door:** Main access point; can be opened, closed, locked, or unlocked.

**HIOs:**
- **Welcome Mat:** May hide keys or clues; supports discovery mechanics.

### Dining Room

**SIOs:**
- **Dining Table:** Central for meals and gatherings; may be used for events or puzzles.
- **Chairs:** Seating for players and NPCs; supports social interactions.

**HIOs:**
- **Tableware (Plates, Cups, Utensils):** Used during meals; may be collected or cleaned.

### Bathroom

**SIOs:**
- **Toilet:** Supports hygiene and humor; can be flushed or searched.
- **Sink:** Used for washing and filling containers.
- **Bathtub:** Can be filled, drained, or entered; supports bathing and hiding.
- **Shower:** Used for bathing; can be turned on or off.
- **Medicine Cabinet:** Storage for medicine and hygiene products.

**HIOs:**
- **Medicine:** Consumable for health or quests.
- **Toothbrush and Toothpaste:** Used for hygiene; may be involved in routines or puzzles.

### Laundry Room

**SIOs:**
- **Washer:** Used for cleaning clothes; supports chores and time-based events.
- **Dryer:** Used for drying clothes; may be involved in puzzles or item retrieval.

**HIOs:**
- **Laundry Basket:** Holds clothes; may hide items or clues.
- **Detergent:** Consumable for washing; may be required for certain actions.

### Living Room

**SIOs:**
- **Couch:** Central seating; can be sat on or searched for hidden items.
- **Bookshelf:** Storage for books and items; supports lore and puzzle-solving.
- **Lamp:** Provides lighting; can be turned on or off.
- **TV:** Entertainment device; can be turned on/off and channel changed.

**HIOs:**
- **Remote Control:** Used to operate the TV; may be found or lost.
- **Book:** Can be read for information, clues, or story progression.
- **Board Game:** Entertainment item; may contain pieces or clues.

### Game Room

**SIOs:**
- **Game Table:** Central for playing games; supports group events.
- **Arcade Machine:** Provides entertainment; may be used for mini-games or puzzles.

**HIOs:**
- **Game Pieces:** Required for board or table games; may be collected or lost.
- **Scoreboard:** Tracks progress in games; may be involved in challenges.

### Outdoor/Utility

**SIOs:**
- **Mailbox:** Container for mail; can be opened or closed and may contain quest items.
- **Garden Hose:** Used for watering plants; can be turned on or off.
- **Grill:** Outdoor cooking appliance; can be turned on/off and used for events.
- **Lawn Mower:** Used for cutting grass; may be involved in chores or puzzles.
- **Door (to outside):** Provides access to the yard or street; can be opened, closed, locked, or unlocked.

**HIOs:**
- **Garden Tools:** Used for gardening tasks; may be required for certain actions.
- **Plants/Flowers:** Can be watered, picked, or used in quests.

### Utility/Other

**SIOs:**
- **Light Switch:** Controls lighting in rooms; can be turned on or off.
- **Thermostat:** Sets room temperature; may affect comfort or trigger events.
- **Phone:** Used to make calls; may be involved in communication-based puzzles.
- **Computer:** Can be used and turned on/off; may provide information or access to systems.
- **Flashlight:** Provides portable light; can be turned on/off and may require batteries.

**HIOs:**
- **Battery:** Consumable resource for powering devices; may be inserted into objects like flashlights.

---

## Strategic Intent and Player Experience

By layering SIOs and HIOs, we create a world that is both approachable and rewarding to explore. SIOs provide the backbone of the player's interaction with the environment, while HIOs offer opportunities for discovery, surprise, and emergent storytelling. The `is_shown` parameter ensures that our backend logic can support both the narrative depth of TAG and the visual clarity of Godot, without compromise.

This strategy is intended to be a living reference as we continue to expand and refine our game world. As new rooms or objects are added, or as gameplay needs evolve, this document should guide our decisions to maintain a consistent, immersive, and engaging player experience. 