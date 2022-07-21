# MobHeads

## Overview

The mob head datapack the Minetown Server uses.
The datapack is a modified version of [VanillaTweaks](https://vanillatweaks.net/) and the rights on all image files belong to them.
This combines the player head drops module with the more mob heads module and adds a random chance to the player head drops.
You can find a list of all available heads [here](HEADS.md).

## (Re-)generating the head overview

This step should be automatically performed by a GitHub action. To do it manually, follow the instructions below.
The scripts for this project are written in python and the required dependencies can be found in [requirements.txt](requirements.txt).
To regenerate the head overview, you need to execute the following command:

```
python3 scripts/generate_head_overview.py
```
