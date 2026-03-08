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
- net assignments
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

Example installation paths (your paths may differ):

```text
...\KiCad\9.0\bin\python.exe
...\KiCad\9.0\bin\kicad-cli.exe

Important:

Run the script with KiCad 9 bundled Python, not system/conda Python, unless your Python can import pcbnew.

kicad-cli is used to export the netlist; pcbnew is used to generate the .kicad_pcb skeleton.

Repository Structure (suggested)
.
├─ tools/
│  └─ sch_to_pcb_skeleton.py
├─ examples/
│  └─ case3/                      (optional demo project)
│     ├─ case3.kicad_sch
│     └─ case3_skeleton.kicad_pcb
└─ README.md
Requirements

You need:

KiCad 9.0

Access to KiCad 9 bundled:

python.exe

kicad-cli.exe

A KiCad schematic file (.kicad_sch) that is already:

annotated (references are not R?, C?, etc.)

assigned footprints

Footprint libraries correctly configured in KiCad via:

global fp-lib-table

project fp-lib-table

If footprints cannot be resolved through KiCad library tables, the output PCB skeleton may miss components.

How it Works (High-Level)

This project uses a two-stage pipeline:

Stage 1 — Schematic → Netlist (via kicad-cli)

The script calls KiCad CLI to export a netlist from .kicad_sch.

The netlist is exported in a machine-readable format (kicadxml) for parsing.

Stage 2 — Netlist → PCB Skeleton (via pcbnew)

Parse the netlist and extract:

component references

footprint identifiers (LIB_NICKNAME:FOOTPRINT_NAME)

net connectivity (ref/pin → net)

Resolve footprint library nicknames using KiCad footprint library tables (fp-lib-table), including common variables like:

${KICAD9_FOOTPRINT_DIR}

${KIPRJMOD}

Create a new pcbnew.BOARD().

Create net objects, load footprints, place them on a simple grid, and assign pads to nets.

Save the final .kicad_pcb skeleton.

Output

The generated .kicad_pcb typically contains:

imported footprints

net assignments (ratsnest / connectivity)

simple initial placement (grid)

To continue PCB design, open the output in KiCad PCB Editor and do:

placement refinement

board outline

routing

copper zones

finishing steps

Run
0) Set your KiCad 9 paths (recommended)

Find these two files in your KiCad 9 installation:

python.exe (KiCad bundled Python)

kicad-cli.exe

Example locations (YOUR PATH MAY BE DIFFERENT):

...\KiCad\9.0\bin\python.exe

...\KiCad\9.0\bin\kicad-cli.exe

1) Windows CMD (template)
"<KICAD9_PYTHON>" "<SCRIPT_PATH>" --sch "<SCHEMATIC_PATH>" --out "<OUTPUT_PCB_PATH>" --kicad-cli "<KICAD9_KICAD_CLI>" --keep-net
2) Windows PowerShell (template)
& "<KICAD9_PYTHON>" "<SCRIPT_PATH>" --sch "<SCHEMATIC_PATH>" --out "<OUTPUT_PCB_PATH>" --kicad-cli "<KICAD9_KICAD_CLI>" --keep-net

Notes:

CMD can directly execute the quoted executable path.

PowerShell requires & before the executable path.

Example (author's working command)
Windows CMD
"D:\app\KiCad\9.0\bin\python.exe" "D:\kicad_test\tools\sch_to_pcb_skeleton.py" --sch "D:\kicad_test\case3\case3.kicad_sch" --out "D:\kicad_test\case3\case3_skeleton.kicad_pcb" --kicad-cli "D:\app\KiCad\9.0\bin\kicad-cli.exe" --keep-net
Windows PowerShell
& "D:\app\KiCad\9.0\bin\python.exe" "D:\kicad_test\tools\sch_to_pcb_skeleton.py" --sch "D:\kicad_test\case3\case3.kicad_sch" --out "D:\kicad_test\case3\case3_skeleton.kicad_pcb" --kicad-cli "D:\app\KiCad\9.0\bin\kicad-cli.exe" --keep-net
CLI Arguments

--sch
Path to the input KiCad schematic (.kicad_sch)

--out
Path to the output PCB skeleton file (.kicad_pcb)

--kicad-cli
Path to KiCad 9 kicad-cli.exe

--keep-net
Keep net assignments in the output PCB skeleton

Common Pitfalls
kicad-cli not found

If you see an error like "kicad-cli is not recognized", pass the full path to kicad-cli.exe (as shown above).

No module named 'pcbnew'

This usually means you used the wrong Python interpreter. Use KiCad 9 bundled Python (the python.exe inside the KiCad installation).

Footprints not imported

If footprints cannot be loaded, check:

schematic symbols have footprints assigned

KiCad footprint library tables (fp-lib-table) are valid

footprint nicknames resolve correctly on your machine

License

MIT License is recommended for this type of utility repository.
