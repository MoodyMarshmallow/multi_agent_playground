import unittest
import json

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
        with open("example.json", "r") as f:
            expected = json.load(f)
        
        actual = memory.convert_to_JSON()
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
