import asyncio
import base64
import io
import json
import shutil
import MinePI
import urllib.request
import PIL.Image
import os
import re
from typing import Iterable, List, Tuple

ENTITY_DIRECTORY = "data/minecraft/loot_tables/entities"
RENDERED_DIRECTORY = "rendered"
OVERVIEW_FILE = "HEADS.md"

async def main():
  shutil.rmtree(RENDERED_DIRECTORY, ignore_errors=True)
  os.makedirs(RENDERED_DIRECTORY)
  
  with open(OVERVIEW_FILE, "w") as overview:
    overview.write("# List of all Mob Heads\n\n")

    for name, url in sorted(find_mob_heads(), key = lambda x: x[0].lower()):
      output_file = f"{RENDERED_DIRECTORY}/{get_output_filename(name)}.png"

      await render_head(url, output_file)

      overview.write(f"### {name}\n\n")
      overview.write(f"![{name}](./{output_file})\n\n")

def find_mob_heads() -> Iterable[Tuple[str, str]]:
  for file in find_loot_tables():
    for nbt in find_skull_nbt(file):
      name = find_name(nbt)
      url = find_texture_url(nbt)
      yield (name, url)
      
def find_loot_tables() -> Iterable[str]:
  for entry in os.listdir(ENTITY_DIRECTORY):
    file = f"{ENTITY_DIRECTORY}/{entry}"

    if os.path.isdir(file):
      # This method is not recursive, because there are some files that are
      # more deeply nested that we don't want to include.
      for inner_entry in os.listdir(file):
        inner_file = f"{file}/{inner_entry}"

        if os.path.isfile(inner_file) and inner_file.endswith(".json"):
          yield inner_file
    elif os.path.isfile(file) and file.endswith(".json"):
      yield file

def find_skull_nbt(file) -> Iterable[str]:
  with open(file, "r") as f:
    root = json.load(f)

    for pool in root["pools"]:
      for entry in pool["entries"]:
        if not "functions" in entry:
          continue

        for function in entry["functions"]:
          if function["function"] != "set_nbt":
            continue

          nbt = str(function["tag"])

          if nbt.startswith("{SkullOwner:{"):
            yield nbt

def find_name(nbt: str) -> str: 
  names = re.findall(r"Name:\"([\w ]+)\"", nbt)

  if len(names) != 1:
    raise KeyError(f"Could not find unambiguous name in '{nbt}'")

  return names[0]

def find_texture_url(nbt: str) -> str:
  texture_values = re.findall(r"Properties:{textures:\[{Value:\"([\w\+/=]+)\"", nbt)

  if len(texture_values) != 1:
    raise KeyError(f"Could not find unambiguous texture value in '{nbt}'")

  root = json.loads(base64.b64decode(texture_values[0]))
  return root["textures"]["SKIN"]["url"]

def get_output_filename(name: str) -> str:
  return name.lower().replace(" ", "_")

async def render_head(url: str, output_file: str) -> str:
  with urllib.request.urlopen(url) as f:
    image = PIL.Image.open(io.BytesIO(f.read()))
    rendered = await MinePI.render_3d_head(skin_image=image, ratio=12, display_hair=True, aa=True)
    rendered.save(output_file, "PNG")

if __name__ == '__main__':
  asyncio.run(main())
