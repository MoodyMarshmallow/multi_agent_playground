"""
Author: Joon Sung Park (joonspk@stanford.edu)

File: spatial_memory.py
Description: Defines the MemoryTree class that serves as the agents' spatial
memory that aids in grounding their behavior in the game world. 
"""
import json
import sys
sys.path.append('../../')

from utils import *
from global_methods import *

class MemoryTree: 
  def __init__(self, f_saved): 
    self.tree = {}
    if check_if_file_exists(f_saved): 
      self.tree = json.load(open(f_saved))


  def print_tree(self): 
    def _print_tree(tree, depth):
      dash = " >" * depth
      if type(tree) == type(list()): 
        if tree:
          print (dash, tree)
        return 

      for key, val in tree.items(): 
        if key: 
          print (dash, key)
        _print_tree(val, depth+1)
    
    _print_tree(self.tree, 0)
    

  def save(self, out_json):
    with open(out_json, "w") as outfile:
      json.dump(self.tree, outfile) 



  def get_str_accessible_sectors(self, curr_world): 
    """
    Returns a summary string of all the arenas that the persona can access 
    within the current sector. 

    Note that there are places a given persona cannot enter. This information
    is provided in the persona sheet. We account for this in this function. 

    INPUT
      None
    OUTPUT 
      A summary string of all the arenas that the persona can access. 
    EXAMPLE STR OUTPUT
      "bedroom, kitchen, dining room, office, bathroom"
    """
    x = ", ".join(list(self.tree[curr_world].keys()))
    return x


  def get_str_accessible_sector_arenas(self, sector): 
    """
    Returns a summary string of all the arenas that the persona can access 
    within the current sector. 

    Note that there are places a given persona cannot enter. This information
    is provided in the persona sheet. We account for this in this function. 

    INPUT
      None
    OUTPUT 
      A summary string of all the arenas that the persona can access. 
    EXAMPLE STR OUTPUT
      "bedroom, kitchen, dining room, office, bathroom"
    """
    curr_world, curr_sector = sector.split(":")
    if not curr_sector: 
      return ""
    x = ", ".join(list(self.tree[curr_world][curr_sector].keys()))
    return x


  def get_str_accessible_arena_game_objects(self, address):
    """
    Returns the objects that are available in the arena. 
    INPUT: 
      address: a string of the form "the_ville:dolores_cafe:counter"
    OUTPUT: 
      a string comma separated list of game object names. 
    """
    # We need to parse the address. 
    if not address: 
      return ""
    address_list = address.split(":")
    if len(address_list) != 3: 
      return ""
    curr_world = address_list[0]
    curr_sector = address_list[1]
    curr_arena = address_list[2]

    try:
      x = ", ".join(list(self.tree[curr_world][curr_sector][curr_arena]))
    except KeyError:
      # Handle the case where the arena doesn't exist
      print(f"KeyError: Arena '{curr_arena}' not found in {curr_world}:{curr_sector}")
      
      # Try to check if there's a "main room" or any other arena in this sector
      try:
        if "main room" in self.tree[curr_world][curr_sector]:
          x = ", ".join(list(self.tree[curr_world][curr_sector]["main room"]))
          print(f"Falling back to 'main room' instead of '{curr_arena}'")
        else:
          # Get the first available arena
          available_arenas = list(self.tree[curr_world][curr_sector].keys())
          if available_arenas:
            first_arena = available_arenas[0]
            x = ", ".join(list(self.tree[curr_world][curr_sector][first_arena]))
            print(f"Falling back to '{first_arena}' instead of '{curr_arena}'")
          else:
            x = ""
      except:
        x = ""
      
    return x


  def get_str_arena_objects(self, world, sector, arena):
    """
    Returns objects in a specific arena without checking accessibility.
    Used as a utility function for fallback handling.
    """
    try:
      return ", ".join(list(self.tree[world][sector][arena]))
    except:
      return ""


if __name__ == '__main__':
  x = f"../../../../environment/frontend_server/storage/the_ville_base_LinFamily/personas/Eddy Lin/bootstrap_memory/spatial_memory.json"
  x = MemoryTree(x)
  x.print_tree()

  print (x.get_str_accessible_sector_arenas("dolores double studio:double studio"))







