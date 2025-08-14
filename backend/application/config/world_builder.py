"""
WorldBuilder Factory
================================
Factory class for building Game objects from YAML world configuration files.

This replaces hardcoded world building with configuration-driven world construction,
enabling multiple scenarios and external customization.
"""

import yaml
import logging
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

from ...infrastructure.game import game_engine as games
from ...domain.entities import Location, Character, Container, Thing
from ...domain.entities.item import (
    EdibleItem, ClothingItem, UtilityItem, BookItem, BeddingItem,
)
# Furniture/fixtures from domain entities
from ...domain.entities.object import (
    Bed, Television, Sink, Chair, Table, Cabinet, Bookshelf, Toilet
)
from .world_config import WorldConfig, WorldConfigurationError, WorldBuildingError


class WorldBuilder:
    """
    Factory class for building Game objects from YAML world configurations.
    
    Supports:
    - Multiple world scenarios via YAML configuration
    - Dynamic location, item, and character creation
    - Complex item relationships (containers with nested items)
    - Full backward compatibility with existing world building
    """
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        
        # Mapping of item type strings to actual classes
        self._item_type_mapping = {
            "edible": EdibleItem,
            "clothing": ClothingItem,
            "utility": UtilityItem,
            "book": BookItem,
            "bedding": BeddingItem,
            "container": Container,
            "furniture": self._create_furniture_item,  # Special handler for furniture
            "electronic": Television  # Default electronic is TV for now
        }
    
    def build_world_from_file(self, config_file_path: str) -> games.Game:
        """
        Build a Game object from a YAML configuration file.
        
        Args:
            config_file_path: Path to the YAML world configuration file
            
        Returns:
            games.Game: Fully constructed game instance
            
        Raises:
            WorldConfigurationError: If configuration file is invalid
            WorldBuildingError: If world construction fails
        """
        try:
            # Load and validate configuration
            config = self._load_world_config(config_file_path)
            
            # Build world from configuration
            return self._build_world_from_config(config)
            
        except Exception as e:
            self._logger.error(f"Failed to build world from file {config_file_path}: {e}")
            raise WorldBuildingError(f"World building failed: {e}") from e
    
    def build_world_from_config(self, config: WorldConfig) -> games.Game:
        """
        Build a Game object from a WorldConfig instance.
        
        Args:
            config: Validated WorldConfig instance
            
        Returns:
            games.Game: Fully constructed game instance
        """
        return self._build_world_from_config(config)
    
    def _load_world_config(self, config_file_path: str) -> WorldConfig:
        """Load and validate world configuration from YAML file."""
        try:
            config_path = Path(config_file_path)
            if not config_path.exists():
                raise WorldConfigurationError(f"Configuration file not found: {config_file_path}")
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            # Validate using Pydantic model
            config = WorldConfig(**config_data)
            self._logger.info(f"Loaded world configuration: {config.game.world_name}")
            
            return config
            
        except yaml.YAMLError as e:
            raise WorldConfigurationError(f"Invalid YAML in configuration file: {e}")
        except Exception as e:
            raise WorldConfigurationError(f"Failed to load configuration: {e}")
    
    def _build_world_from_config(self, config: WorldConfig) -> games.Game:
        """Build complete world from configuration."""
        self._logger.info(f"Building world: {config.game.world_name}")
        
        # Create locations
        locations = self._create_locations(config)
        
        # Connect locations
        self._connect_locations(config, locations)
        
        # Create and place items
        self._create_and_place_items(config, locations)
        
        # Create characters
        player_character = self._create_player_character()
        npc_characters = self._create_characters(config, locations)
        
        # Build game object
        starting_location = locations[config.game.starting_location]
        game = games.Game(starting_location, player_character, characters=npc_characters)
        
        self._logger.info(f"Successfully built world '{config.game.world_name}' with {len(locations)} locations, {len(config.items)} items, {len(npc_characters)} characters")
        
        return game
    
    def _create_locations(self, config: WorldConfig) -> Dict[str, Location]:
        """Create all locations from configuration."""
        locations = {}
        
        for location_id, location_config in config.locations.items():
            location = Location(location_config.name, location_config.description)
            locations[location_id] = location
            self._logger.debug(f"Created location: {location_id}")
        
        return locations
    
    def _connect_locations(self, config: WorldConfig, locations: Dict[str, Location]) -> None:
        """Connect locations according to configuration."""
        for location_id, location_config in config.locations.items():
            current_location = locations[location_id]
            
            for direction, connected_location_id in location_config.connections.items():
                connected_location = locations[connected_location_id]
                current_location.add_connection(direction, connected_location)
                
                self._logger.debug(f"Connected {location_id} -> {direction} -> {connected_location_id}")
    
    def _create_and_place_items(self, config: WorldConfig, locations: Dict[str, Location]) -> None:
        """Create all items and place them in locations."""
        for item_config in config.items:
            try:
                # Create the main item
                item = self._create_item(item_config.name, item_config.display_name, 
                                       item_config.description, item_config.item_type, 
                                       item_config.properties)
                
                # Handle contained items if this is a container
                if item_config.contained_items and isinstance(item, Container):
                    for contained_config in item_config.contained_items:
                        contained_item = self._create_item(
                            contained_config.name, contained_config.display_name,
                            contained_config.description, contained_config.item_type,
                            contained_config.properties
                        )
                        item.add_item(contained_item)
                        self._logger.debug(f"Added {contained_config.name} to container {item_config.name}")
                
                # Place item in location
                location = locations[item_config.location]
                location.add_item(item)
                
                self._logger.debug(f"Created and placed item: {item_config.name} in {item_config.location}")
                
            except Exception as e:
                self._logger.error(f"Failed to create item {item_config.name}: {e}")
                raise WorldBuildingError(f"Item creation failed: {item_config.name}") from e
    
    def _create_item(self, name: str, display_name: str, description: str, 
                    item_type: str, properties: Any) -> Thing:
        """Create a single item with the specified type and properties."""
        # Get the item class for this type
        item_class_or_handler = self._item_type_mapping.get(item_type)
        if not item_class_or_handler:
            raise WorldBuildingError(f"Unknown item type: {item_type}")
        
        # Handle special cases
        if callable(item_class_or_handler) and item_class_or_handler == self._create_furniture_item:
            item = self._create_furniture_item(name, display_name, description, properties)
        else:
            # Standard item creation
            item = self._create_standard_item(item_class_or_handler, name, display_name, 
                                           description, properties)
        
        # Apply common properties
        self._apply_item_properties(item, properties)
        
        return item
    
    def _create_standard_item(self, item_class, name: str, display_name: str, 
                            description: str, properties: Any) -> Any:
        """Create a standard item using its class constructor."""
        try:
            # Handle different item types with specific constructor arguments
            if item_class == EdibleItem:
                return EdibleItem(name, display_name, description)
            
            elif item_class == ClothingItem:
                clothing_type = properties.clothing_type if properties else "generic"
                material = properties.material if properties else "fabric"
                return ClothingItem(name, display_name, description, 
                                  clothing_type=clothing_type, material=material)
            
            elif item_class == UtilityItem:
                utility_type = properties.utility_type if properties else "tool"
                return UtilityItem(name, display_name, description, utility_type=utility_type)
            
            elif item_class == BookItem:
                title = properties.book_title if properties else display_name
                author = properties.book_author if properties else "Unknown"
                return BookItem(name, display_name, title=title, author=author)
            
            elif item_class == BeddingItem:
                bedding_type = properties.bedding_type if properties else "sheet"
                material = properties.material if properties else "cotton"
                color = properties.color if properties else "white"
                return BeddingItem(name, display_name, description,
                                 bedding_type=bedding_type, material=material, color=color)
            
            elif item_class == Container:
                is_openable = properties.is_openable if properties else True
                is_open = properties.is_open if properties else False
                return Container(name, description, is_openable=is_openable, is_open=is_open)
            
            elif item_class == Television:
                return Television(name, description)
            
            elif item_class == Sink:
                return Sink(name, description)
            
            else:
                # Generic Thing creation
                return item_class(name, description)
                
        except Exception as e:
            self._logger.error(f"Failed to create {item_class.__name__} '{name}': {e}")
            raise
    
    def _create_furniture_item(self, name: str, display_name: str, 
                              description: str, properties: Any) -> Thing:
        """Create furniture items with appropriate specialized classes."""
        # Map furniture items to specific classes based on name/properties
        name_lower = name.lower()
        
        if "bed" in name_lower:
            return Bed(name, description)
        elif "chair" in name_lower or "couch" in name_lower:
            return Chair(name, description)
        elif "table" in name_lower:
            return Table(name, description)
        elif "cabinet" in name_lower:
            return Cabinet(name, description)
        elif "bookshelf" in name_lower:
            return Bookshelf(name, description)
        elif "toilet" in name_lower:
            return Toilet(name, description)
        else:
            # Generic furniture - use Chair as base furniture class
            return Chair(name, description)
    
    def _apply_item_properties(self, item: Any, properties: Any) -> None:
        """Apply properties to an item after creation."""
        if not properties:
            return
        
        # Apply standard properties
        for prop_name, prop_value in [
            ("color", properties.color),
            ("material", properties.material),
            ("size", properties.size),
            ("weight", properties.weight),
            ("temperature", properties.temperature),
            ("is_gettable", properties.is_gettable),
        ]:
            if prop_value is not None:
                if hasattr(item, 'set_property'):
                    item.set_property(prop_name, prop_value)
                else:
                    setattr(item, prop_name, prop_value)
        
        # Apply special properties
        if properties.is_made is not None:
            if hasattr(item, 'set_property'):
                item.set_property("is_made", properties.is_made)
            else:
                setattr(item, "is_made", properties.is_made)
        
        # Handle quilt_color from custom properties
        if hasattr(properties, 'custom_properties') and properties.custom_properties:
            quilt_color = properties.custom_properties.get('quilt_color')
            if quilt_color is not None and hasattr(item, 'set_property'):
                item.set_property("quilt_color", quilt_color)
        
        # Apply custom properties
        if hasattr(properties, 'custom_properties') and properties.custom_properties:
            for custom_prop, custom_value in properties.custom_properties.items():
                if hasattr(item, 'set_property'):
                    item.set_property(custom_prop, custom_value)
                else:
                    setattr(item, custom_prop, custom_value)
    
    def _create_player_character(self) -> Character:
        """Create the default player character."""
        return Character(
            name="Player",
            description="An explorer in a large, modern house.",
            persona="I am curious and love to explore new places."
        )
    
    def _create_characters(self, config: WorldConfig, locations: Dict[str, Location]) -> List[Character]:
        """Create and place NPC characters from configuration."""
        characters = []
        
        for char_config in config.characters:
            if char_config.is_npc:
                character = Character(
                    name=char_config.name,
                    description=char_config.description,
                    persona=char_config.persona or f"I am {char_config.display_name}."
                )
                
                # Apply custom properties
                for prop_name, prop_value in char_config.properties.items():
                    setattr(character, prop_name, prop_value)
                
                # Place character in initial location
                initial_location = locations[char_config.initial_location]
                initial_location.add_character(character)
                
                characters.append(character)
                self._logger.debug(f"Created character: {char_config.name} in {char_config.initial_location}")
        
        return characters


# Exception classes for world building errors
class WorldBuilderError(Exception):
    """Base exception for WorldBuilder errors."""
    pass