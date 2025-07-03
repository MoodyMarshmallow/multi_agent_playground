import unittest
import json
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent.parent  # Go up one level from tests/ to backend/
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from spatial import SpatialMemory


class SpatialTestCase(unittest.TestCase):
    def test_convert_to_JSON(self):
        memory = SpatialMemory({
            "nodes": [
                "kitchen", "sink", "cutting_board", "oven", "stove",
                "bedroom", "bed", "blanket", "mattress", "lamp",
                "living_room", "couch", "TV", "fireplace",
                "first_floor", "second_floor"
            ],
            "edges": [
                ("kitchen", ["sink", "cutting_board", "oven", "stove"]),
                ("bedroom", ["bed", "blanket", "mattress", "lamp"]),
                ("living_room", ["couch", "TV", "fireplace"]),
                ("first_floor", ["kitchen", "living_room"]),
                ("second_floor", ["bedroom"])
            ],
        })
        
        # Load expected result from example.json
        with open("../example.json", "r") as f:
            expected = json.load(f)
        
        actual = memory.convert_to_JSON()
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
