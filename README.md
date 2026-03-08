# kicad-sch-to-pcb-skeleton

Generate a **KiCad PCB skeleton** from a **KiCad schematic** using **kicad-cli** and **pcbnew**.

> This project generates an initial **PCB skeleton** (`.kicad_pcb`) from a KiCad schematic (`.kicad_sch`).
> It is **not** intended to reconstruct a fully routed or finished PCB.

---

## Overview

This project provides a standalone Python workflow for generating a basic KiCad PCB skeleton from a schematic.

The generated PCB contains:

- footprints
- net assignments
- simple initial placement

The generated PCB does **not** include:

- final component placement
- routing / tracks
- vias
- copper pours
- final board outline
- detailed silkscreen tuning

So this tool is meant to produce a **starting board structure**, not a completed PCB.

---

## Tested Environment

This project is currently tested with:

- **KiCad 9.0**
- **Windows**
- **KiCad 9 bundled Python**
- **KiCad 9 bundled `kicad-cli.exe`**

Example paths:

```text
D:\app\KiCad\9.0\bin\python.exe
D:\app\KiCad\9.0\bin\kicad-cli.exe
