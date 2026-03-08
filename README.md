# kicad-sch-to-pcb-skeleton

A standalone Python tool that generates an initial **KiCad PCB skeleton** from a **KiCad schematic**.

This project does **not** try to reconstruct a fully routed PCB.  
Instead, it focuses on generating a **starting PCB board** containing:

- footprints
- net connections
- initial component placement

It is designed for workflows where you want to go from **schematic** to a **basic `.kicad_pcb` skeleton** without manually opening KiCad PCB Editor and clicking update actions.

---

## What this project does

Given a KiCad schematic file (`.kicad_sch`), this tool:

1. uses `kicad-cli` to export a netlist
2. parses component and net information from the netlist
3. resolves footprint library nicknames via `fp-lib-table`
4. uses `pcbnew` Python bindings to create a new board
5. loads footprints onto the board
6. assigns pads to the correct nets
7. writes out a new `.kicad_pcb` file

---

## What this project does **not** do

This project generates a **PCB skeleton**, not a finished PCB.

It does **not** automatically reconstruct:

- final component placement
- routing / tracks
- vias
- copper pours
- final board outline
- detailed silkscreen tuning

So the output should be understood as a **starting PCB structure**, not a fully finished board.

---

## Workflow

The current workflow is:

```text
KiCad schematic (.kicad_sch)
        ↓
kicad-cli export netlist (kicadxml)
        ↓
Python parses netlist
        ↓
pcbnew creates BOARD
        ↓
load footprints + create nets + place footprints
        ↓
output .kicad_pcb skeleton
