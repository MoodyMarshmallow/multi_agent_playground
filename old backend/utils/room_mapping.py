# utils/room_mapping.py

# Create a mapping from tile to room; currently we use this because we have a small number of rooms and we can afford to do this
# this is space-intensive, but time-efficient
def build_tile_to_room_map(env_map: dict) -> dict:
    tile_to_room = {}
    def walk(obj, room_path):
        if isinstance(obj, dict):
            for key, val in obj.items():
                if key == "shape":
                    for coord in val:
                        tile_to_room[tuple(coord)] = room_path[-1]  # Use last room name
                elif key == "interact":
                    continue
                else:
                    walk(val, room_path + [key])
    walk(env_map, [])
    return tile_to_room
