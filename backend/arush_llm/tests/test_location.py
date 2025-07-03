"""
Unit Tests for Location Module
==============================
Tests for LocationTracker with performance validation.
"""

import pytest
import time
import json
from pathlib import Path

from arush_llm.agent.location import LocationTracker


class TestLocationTracker:
    """Test suite for LocationTracker implementation."""
    
    @pytest.mark.unit
    def test_initialization(self, temp_dir, sample_object_registry):
        """Test LocationTracker initialization."""
        tracker = LocationTracker(
            agent_id="test_agent",
            data_dir=temp_dir,
            object_registry=sample_object_registry
        )
        
        assert tracker.agent_id == "test_agent"
        assert tracker.data_dir == temp_dir
        assert tracker.object_registry == sample_object_registry
        assert tracker.current_position == [0, 0]  # Default position
        assert tracker.current_room == "unknown"
        assert len(tracker.spatial_index) == 0
        assert len(tracker.room_cache) == 0
    
    @pytest.mark.unit
    def test_update_position(self, temp_dir, sample_object_registry):
        """Test position updating."""
        tracker = LocationTracker("test_agent", temp_dir, sample_object_registry)
        
        # Update to kitchen position
        tracker.update_position([21, 8], "kitchen")
        
        assert tracker.current_position == [21, 8]
        assert tracker.current_room == "kitchen"
        
        # Check spatial index
        position_key = "21,8"
        assert position_key in tracker.spatial_index
        assert tracker.spatial_index[position_key]["room"] == "kitchen"
    
    @pytest.mark.unit
    def test_get_nearby_objects(self, temp_dir, sample_object_registry):
        """Test getting nearby objects."""
        tracker = LocationTracker("test_agent", temp_dir, sample_object_registry)
        
        # Position agent near coffee machine
        tracker.update_position([21, 8], "kitchen")
        
        # Get nearby objects
        nearby = tracker.get_nearby_objects(radius=2)
        
        # Should include coffee_machine and refrigerator
        assert len(nearby) >= 1
        nearby_names = [obj["name"] for obj in nearby]
        assert "coffee_machine" in nearby_names
    
    @pytest.mark.unit
    def test_get_objects_in_room(self, temp_dir, sample_object_registry):
        """Test getting objects in current room."""
        tracker = LocationTracker("test_agent", temp_dir, sample_object_registry)
        
        # Update to kitchen
        tracker.update_position([21, 8], "kitchen")
        
        # Get objects in kitchen
        room_objects = tracker.get_objects_in_room("kitchen")
        
        # Should find kitchen objects
        assert len(room_objects) >= 2
        object_names = [obj["name"] for obj in room_objects]
        assert "coffee_machine" in object_names
        assert "refrigerator" in object_names
    
    @pytest.mark.unit
    def test_get_movement_options(self, temp_dir, sample_object_registry):
        """Test getting movement options."""
        tracker = LocationTracker("test_agent", temp_dir, sample_object_registry)
        
        # Set up some spatial mapping
        tracker.update_position([21, 8], "kitchen")
        tracker.spatial_index["21,7"] = {"room": "kitchen", "blocked": False}
        tracker.spatial_index["21,9"] = {"room": "dining_room", "blocked": False}
        tracker.spatial_index["20,8"] = {"room": "kitchen", "blocked": True}  # Blocked
        
        # Get movement options
        options = tracker.get_movement_options()
        
        assert len(options) > 0
        # Should include valid directions
        assert any(opt["direction"] == "north" for opt in options if opt["position"] == [21, 7])
        assert any(opt["direction"] == "south" for opt in options if opt["position"] == [21, 9])
        # Should not include blocked positions
        assert not any(opt["position"] == [20, 8] for opt in options)
    
    @pytest.mark.unit
    def test_calculate_distance(self, temp_dir, sample_object_registry):
        """Test distance calculation."""
        tracker = LocationTracker("test_agent", temp_dir, sample_object_registry)
        
        # Test Manhattan distance
        dist = tracker.calculate_distance([0, 0], [3, 4])
        assert dist == 7  # |3-0| + |4-0| = 7
        
        # Test same position
        dist = tracker.calculate_distance([5, 5], [5, 5])
        assert dist == 0
        
        # Test negative coordinates
        dist = tracker.calculate_distance([-1, -1], [1, 1])
        assert dist == 4  # |1-(-1)| + |1-(-1)| = 4
    
    @pytest.mark.unit
    def test_find_path_to_room(self, temp_dir, sample_object_registry):
        """Test pathfinding to rooms."""
        tracker = LocationTracker("test_agent", temp_dir, sample_object_registry)
        
        # Set up spatial mapping for pathfinding
        tracker.update_position([21, 8], "kitchen")
        
        # Add room mapping
        tracker.room_cache["kitchen"] = {
            "tiles": [[21, 8], [21, 7], [22, 8]],
            "exits": {"north": [21, 6]},
            "objects": ["coffee_machine", "refrigerator"]
        }
        
        tracker.room_cache["office"] = {
            "tiles": [[20, 10], [21, 10]],
            "exits": {"south": [21, 9]},
            "objects": ["desk", "computer"]
        }
        
        # Find path to office
        path = tracker.find_path_to_room("office")
        
        assert len(path) > 0
        assert path[-1] in tracker.room_cache["office"]["tiles"]
    
    @pytest.mark.unit
    def test_get_adjacent_rooms(self, temp_dir, sample_object_registry):
        """Test getting adjacent rooms."""
        tracker = LocationTracker("test_agent", temp_dir, sample_object_registry)
        
        # Set up room mapping
        tracker.update_position([21, 8], "kitchen")
        tracker.room_cache["kitchen"] = {
            "tiles": [[21, 8], [21, 7], [22, 8]],
            "adjacent_rooms": ["dining_room", "living_room"],
            "objects": []
        }
        
        # Get adjacent rooms
        adjacent = tracker.get_adjacent_rooms()
        
        assert len(adjacent) == 2
        assert "dining_room" in adjacent
        assert "living_room" in adjacent
    
    @pytest.mark.unit
    def test_is_position_accessible(self, temp_dir, sample_object_registry):
        """Test position accessibility checking."""
        tracker = LocationTracker("test_agent", temp_dir, sample_object_registry)
        
        # Set up spatial index
        tracker.spatial_index["21,8"] = {"room": "kitchen", "blocked": False}
        tracker.spatial_index["21,9"] = {"room": "kitchen", "blocked": True}
        
        # Test accessible position
        assert tracker.is_position_accessible([21, 8]) is True
        
        # Test blocked position
        assert tracker.is_position_accessible([21, 9]) is False
        
        # Test unknown position (should default to accessible)
        assert tracker.is_position_accessible([25, 25]) is True
    
    @pytest.mark.unit
    def test_track_movement_history(self, temp_dir, sample_object_registry):
        """Test movement history tracking."""
        tracker = LocationTracker("test_agent", temp_dir, sample_object_registry)
        
        # Move through several positions
        positions = [
            ([21, 8], "kitchen"),
            ([21, 7], "kitchen"),
            ([21, 6], "hallway"),
            ([20, 6], "living_room")
        ]
        
        for pos, room in positions:
            tracker.update_position(pos, room)
        
        # Check movement history
        history = tracker.get_movement_history(limit=3)
        
        assert len(history) <= 3
        assert history[0]["position"] == [20, 6]  # Most recent
        assert history[0]["room"] == "living_room"
    
    @pytest.mark.unit
    def test_cache_management(self, temp_dir, sample_object_registry):
        """Test cache management."""
        tracker = LocationTracker("test_agent", temp_dir, sample_object_registry)
        
        # Add data to caches
        tracker.room_cache["kitchen"] = {"tiles": [[21, 8]], "objects": []}
        tracker.spatial_index["21,8"] = {"room": "kitchen", "blocked": False}
        
        # Clear caches
        tracker.clear_cache()
        
        assert len(tracker.room_cache) == 0
        assert len(tracker.spatial_index) == 0
    
    @pytest.mark.unit
    def test_proximity_detection(self, temp_dir, sample_object_registry):
        """Test proximity detection."""
        tracker = LocationTracker("test_agent", temp_dir, sample_object_registry)
        
        # Position agent
        tracker.update_position([21, 8], "kitchen")
        
        # Test proximity to coffee machine at [21, 8]
        is_near = tracker.is_near_object("coffee_machine", max_distance=1)
        assert is_near is True
        
        # Test proximity to desk at [20, 10] (distance = 3)
        is_near = tracker.is_near_object("desk", max_distance=2)
        assert is_near is False
        
        is_near = tracker.is_near_object("desk", max_distance=5)
        assert is_near is True
    
    @pytest.mark.performance
    def test_location_performance(self, temp_dir, sample_object_registry, performance_timer):
        """Test location tracking performance."""
        tracker = LocationTracker("test_agent", temp_dir, sample_object_registry)
        
        # Test position update performance
        performance_timer.start()
        for i in range(1000):
            tracker.update_position([i % 50, i % 50], f"room_{i % 10}")
        update_time = performance_timer.stop()
        
        # Test nearby object search performance
        tracker.update_position([21, 8], "kitchen")
        performance_timer.start()
        for i in range(100):
            tracker.get_nearby_objects(radius=5)
        search_time = performance_timer.stop()
        
        # Test movement options performance
        performance_timer.start()
        for i in range(100):
            tracker.get_movement_options()
        movement_time = performance_timer.stop()
        
        # Performance assertions
        assert update_time / 1000 < 0.001    # Less than 1ms per update
        assert search_time / 100 < 0.001     # Less than 1ms per search
        assert movement_time / 100 < 0.001   # Less than 1ms per movement calc
        
        print(f"Position update performance: {update_time/1000:.6f}s per operation")
        print(f"Object search performance: {search_time/100:.6f}s per operation")
        print(f"Movement options performance: {movement_time/100:.6f}s per operation")
    
    @pytest.mark.unit
    def test_persistence(self, temp_dir, sample_object_registry):
        """Test location data persistence."""
        tracker = LocationTracker("test_agent", temp_dir, sample_object_registry)
        
        # Set up some data
        tracker.update_position([21, 8], "kitchen")
        tracker.room_cache["kitchen"] = {
            "tiles": [[21, 8], [22, 8]],
            "objects": ["coffee_machine"]
        }
        
        # Save data
        tracker.save_location_data()
        
        # Create new tracker and load data
        new_tracker = LocationTracker("test_agent", temp_dir, sample_object_registry)
        new_tracker.load_location_data()
        
        # Verify data persistence
        assert new_tracker.current_position == [21, 8]
        assert new_tracker.current_room == "kitchen"
        assert "kitchen" in new_tracker.room_cache
    
    @pytest.mark.unit
    def test_room_mapping(self, temp_dir, sample_object_registry):
        """Test room mapping functionality."""
        tracker = LocationTracker("test_agent", temp_dir, sample_object_registry)
        
        # Map a room
        room_data = {
            "tiles": [[21, 8], [21, 7], [22, 8], [22, 7]],
            "exits": {"north": [21, 6], "east": [23, 8]},
            "objects": ["coffee_machine", "refrigerator"],
            "adjacent_rooms": ["dining_room", "hallway"]
        }
        
        tracker.map_room("kitchen", room_data)
        
        # Verify room is mapped
        assert "kitchen" in tracker.room_cache
        assert tracker.room_cache["kitchen"]["tiles"] == room_data["tiles"]
        assert tracker.room_cache["kitchen"]["objects"] == room_data["objects"]
        
        # Test getting room info
        room_info = tracker.get_room_info("kitchen")
        assert room_info["tiles"] == room_data["tiles"]
        assert room_info["objects"] == room_data["objects"]
    
    @pytest.mark.unit
    def test_spatial_queries(self, temp_dir, sample_object_registry):
        """Test spatial query functionality."""
        tracker = LocationTracker("test_agent", temp_dir, sample_object_registry)
        
        # Set up spatial data
        positions = [
            ([20, 8], "kitchen"),
            ([21, 8], "kitchen"),
            ([22, 8], "kitchen"),
            ([21, 10], "office")
        ]
        
        for pos, room in positions:
            tracker.spatial_index[f"{pos[0]},{pos[1]}"] = {
                "room": room,
                "blocked": False,
                "last_visited": "01T15:30:00"
            }
        
        # Query positions in kitchen
        kitchen_positions = tracker.get_positions_in_room("kitchen")
        assert len(kitchen_positions) == 3
        
        # Query positions in radius
        tracker.update_position([21, 8], "kitchen")
        nearby_positions = tracker.get_positions_in_radius([21, 8], radius=2)
        assert len(nearby_positions) >= 3
        
        # Test position filtering
        accessible_positions = tracker.get_accessible_positions_in_radius([21, 8], radius=3)
        assert len(accessible_positions) > 0
        assert all(not pos["blocked"] for pos in accessible_positions)
    
    @pytest.mark.unit
    def test_error_handling(self, temp_dir, sample_object_registry):
        """Test error handling in location operations."""
        tracker = LocationTracker("test_agent", temp_dir, sample_object_registry)
        
        # Test with invalid object name
        nearby = tracker.get_nearby_objects(radius=5)
        is_near = tracker.is_near_object("nonexistent_object", max_distance=5)
        assert is_near is False
        
        # Test with invalid room
        room_info = tracker.get_room_info("nonexistent_room")
        assert room_info == {}
        
        # Test pathfinding to nonexistent room
        path = tracker.find_path_to_room("nonexistent_room")
        assert len(path) == 0
        
        # Test loading non-existent data file
        tracker.load_location_data()  # Should not raise error 