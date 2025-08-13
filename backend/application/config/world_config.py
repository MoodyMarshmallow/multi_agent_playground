"""
World Configuration Schema
======================================
Pydantic models for defining game worlds, locations, items, and characters 
through YAML configuration files.

This enables external world configuration, replacing hardcoded world building
in the text adventure games framework.
"""

from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class ItemType(str, Enum):
    """Types of items that can be created in the world."""
    EDIBLE = "edible"
    CLOTHING = "clothing"
    UTILITY = "utility"
    BOOK = "book"
    BEDDING = "bedding"
    CONTAINER = "container"
    FURNITURE = "furniture"
    ELECTRONIC = "electronic"


class LocationConfig(BaseModel):
    """Configuration for a single location/room in the world."""
    name: str = Field(..., description="Display name of the location")
    description: str = Field(..., description="Detailed description of the location")
    connections: Dict[str, str] = Field(default_factory=dict, description="Direction -> location name mapping")
    
    class Config:
        extra = "forbid"


class ItemPropertyConfig(BaseModel):
    """Configuration for item properties."""
    color: Optional[str] = None
    material: Optional[str] = None
    size: Optional[str] = None
    weight: Optional[str] = None
    temperature: Optional[str] = None
    is_open: Optional[bool] = None
    is_openable: Optional[bool] = None
    is_locked: Optional[bool] = None
    is_lockable: Optional[bool] = None
    is_gettable: Optional[bool] = None
    is_made: Optional[bool] = None
    
    # Item type specific properties
    clothing_type: Optional[str] = None  # For clothing items
    bedding_type: Optional[str] = None   # For bedding items
    utility_type: Optional[str] = None   # For utility items
    book_title: Optional[str] = None     # For books
    book_author: Optional[str] = None    # For books
    
    # Custom properties
    custom_properties: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        extra = "allow"  # Allow additional custom properties


class ContainedItemConfig(BaseModel):
    """Configuration for items contained within containers."""
    name: str = Field(..., description="Name/ID of the contained item")
    display_name: str = Field(..., description="Display name of the item")
    description: str = Field(..., description="Description of the item")
    item_type: ItemType = Field(..., description="Type of the item")
    properties: ItemPropertyConfig = Field(default_factory=ItemPropertyConfig)
    
    class Config:
        extra = "forbid"


class ItemConfig(BaseModel):
    """Configuration for a single item in the world."""
    name: str = Field(..., description="Unique name/ID of the item")
    display_name: str = Field(..., description="Display name of the item")
    description: str = Field(..., description="Detailed description of the item")
    item_type: ItemType = Field(..., description="Type of the item")
    location: str = Field(..., description="Initial location where item is placed")
    properties: ItemPropertyConfig = Field(default_factory=ItemPropertyConfig)
    contained_items: List[ContainedItemConfig] = Field(default_factory=list, description="Items contained within this item (if it's a container)")
    
    class Config:
        extra = "forbid"


class CharacterConfig(BaseModel):
    """Configuration for NPCs and characters in the world."""
    name: str = Field(..., description="Name/ID of the character")
    display_name: str = Field(..., description="Display name of the character")
    description: str = Field(..., description="Description of the character")
    initial_location: str = Field(..., description="Starting location for the character")
    persona: Optional[str] = Field(None, description="Character personality/behavior description")
    is_npc: bool = Field(True, description="Whether this is an NPC or player character")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Custom character properties")
    
    class Config:
        extra = "forbid"


class GameConfig(BaseModel):
    """Configuration for game-level settings."""
    max_turns_per_session: int = Field(1000, description="Maximum turns allowed per game session")
    starting_location: str = Field(..., description="Starting location name for players")
    world_name: str = Field(..., description="Name of this world/scenario")
    world_description: Optional[str] = Field(None, description="Description of this world")
    
    # Win/lose conditions (future expansion)
    win_conditions: List[str] = Field(default_factory=list, description="Win condition definitions")
    lose_conditions: List[str] = Field(default_factory=list, description="Lose condition definitions")
    
    class Config:
        extra = "forbid"


class WorldConfig(BaseModel):
    """Complete world configuration including locations, items, characters, and game settings."""
    game: GameConfig = Field(..., description="Game-level configuration")
    locations: Dict[str, LocationConfig] = Field(..., description="Map of location_id -> LocationConfig")
    items: List[ItemConfig] = Field(default_factory=list, description="List of all items in the world")
    characters: List[CharacterConfig] = Field(default_factory=list, description="List of all characters/NPCs")
    
    @validator('locations')
    def validate_location_connections(cls, locations):
        """Validate that location connections reference existing locations."""
        location_names = set(locations.keys())
        
        for loc_id, location in locations.items():
            for direction, connected_location in location.connections.items():
                if connected_location not in location_names:
                    raise ValueError(f"Location '{loc_id}' connects to non-existent location '{connected_location}'")
        
        return locations
    
    @validator('items')
    def validate_item_locations(cls, items, values):
        """Validate that items are placed in existing locations."""
        if 'locations' not in values:
            return items
            
        location_names = set(values['locations'].keys())
        
        for item in items:
            if item.location not in location_names:
                raise ValueError(f"Item '{item.name}' placed in non-existent location '{item.location}'")
        
        return items
    
    @validator('characters')
    def validate_character_locations(cls, characters, values):
        """Validate that characters are placed in existing locations."""
        if 'locations' not in values:
            return characters
            
        location_names = set(values['locations'].keys())
        
        for character in characters:
            if character.initial_location not in location_names:
                raise ValueError(f"Character '{character.name}' placed in non-existent location '{character.initial_location}'")
        
        return characters
    
    @validator('game')
    def validate_game_starting_location(cls, game_config, values):
        """Validate that game starting location exists."""
        if 'locations' not in values:
            return game_config
            
        location_names = set(values['locations'].keys())
        
        if game_config.starting_location not in location_names:
            raise ValueError(f"Game starting location '{game_config.starting_location}' does not exist")
        
        return game_config
    
    class Config:
        extra = "forbid"


# Exception classes for world configuration errors
class WorldConfigurationError(Exception):
    """Base exception for world configuration errors."""
    pass


class WorldValidationError(WorldConfigurationError):
    """Raised when world configuration validation fails."""
    pass


class WorldBuildingError(WorldConfigurationError):
    """Raised when world building from configuration fails."""
    pass