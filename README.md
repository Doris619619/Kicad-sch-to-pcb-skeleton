# kicad-sch-to-pcb-skeleton

**Repository description:**  
Generate a KiCad PCB skeleton from a schematic using `kicad-cli` and `pcbnew`.

---

## Overview

This repository provides a standalone Python workflow for generating an initial **KiCad PCB skeleton** (`.kicad_pcb`) from a **KiCad schematic** (`.kicad_sch`).

The generated PCB is intended to be a **starting board structure**, not a fully finished PCB.

### What this project does

Given a KiCad schematic, this tool generates a PCB skeleton containing:

- footprints
- net assignments (ratsnest connectivity)
- simple initial component placement (grid placement)

### What this project does not do

This project does **not** reconstruct a fully finished PCB.  
The generated result does **not** include:

- final placement refinement
- routed traces
- vias
- copper pours
- final board outline
- polished silkscreen layout

In other words, this project generates a **PCB skeleton**, not a fully routed production-ready PCB.

---

## Tested Environment

This project is currently tested on:

- **KiCad 9.0**
- **Windows**
- **KiCad 9 bundled Python**
- **KiCad 9 bundled `kicad-cli.exe`**

---

## Requirements

You need:

1. **KiCad 9.0 installed**
2. Access to these two executables inside the KiCad installation:
   - `python.exe` (KiCad bundled Python, includes `pcbnew`)
   - `kicad-cli.exe` (KiCad CLI tool)
3. A valid KiCad schematic file (`.kicad_sch`) that is ready for export:
   - components are annotated (no `R?`, `C?`, etc.)
   - footprints are assigned
4. Footprint libraries properly configured in KiCad:
   - global `fp-lib-table` and/or project `fp-lib-table` should resolve footprint nicknames correctly

> Important: Do **not** use system Python / Conda Python unless it can `import pcbnew`.  
> This tool is intended to run with **KiCad’s bundled Python**.

---

## Repository Structure (recommended)

```text
.
├─ tools/
│  └─ sch_to_pcb_skeleton.py
├─ examples/
│  └─ case3/
│     ├─ case3.kicad_sch
│     └─ case3_skeleton.kicad_pcb
└─ README.md
