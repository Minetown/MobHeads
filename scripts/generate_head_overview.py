import asyncio
import base64
import io
import json
import shutil
from minepi import Skin
import urllib.request
import PIL.Image
import os
from typing import Iterable, Tuple

ENTITY_DIRECTORY = "data/more_mob_heads/loot_table/entities"
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
    yield from find_skull_nbt(file)
      
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

def find_skull_nbt(file) -> Iterable[Tuple[str, str]]:
  with open(file, "r") as f:
    root = json.load(f)

    for pool in root["pools"]:
      for entry in pool["entries"]:
        if not "functions" in entry:
          continue

        for function in entry["functions"]:
          if function["function"] != "set_components":
            continue

          components = function["components"]

          if "minecraft:profile" not in components or "minecraft:item_name" not in components:
            continue

          textures = components["minecraft:profile"]["properties"][0]["value"]
          decoded_textures = json.loads(base64.b64decode(textures))
          url = decoded_textures["textures"]["SKIN"]["url"]

          name = components["minecraft:item_name"].replace("\"", "")

          yield (name, url)

def get_output_filename(name: str) -> str:
  return name.lower().replace(" ", "_")

async def render_head(url: str, output_file: str) -> str:
  with urllib.request.urlopen(url) as f:
    image = PIL.Image.open(io.BytesIO(f.read()))
    skin = Skin(raw_skin=image)
    rendered = await skin.render_head(vr=-25, ratio=12, display_hair=True, aa=True)
    rendered.save(output_file, "PNG")

if __name__ == '__main__':
  asyncio.run(main())
