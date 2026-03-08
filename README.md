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
- simple initial component placement

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

Example installation paths:

```text
D:\app\KiCad\9.0\bin\python.exe
D:\app\KiCad\9.0\bin\kicad-cli.exe

## Run

### 0) Set your KiCad 9 paths (recommended)

Find these two files in your KiCad 9 installation:

- `python.exe` (KiCad bundled Python)
- `kicad-cli.exe`

Example locations (YOUR PATH MAY BE DIFFERENT):

- `...\KiCad\9.0\bin\python.exe`
- `...\KiCad\9.0\bin\kicad-cli.exe`

---

### 1) Windows CMD (template)

```cmd
"<KICAD9_PYTHON>" "<SCRIPT_PATH>" --sch "<SCHEMATIC_PATH>" --out "<OUTPUT_PCB_PATH>" --kicad-cli "<KICAD9_KICAD_CLI>" --keep-net
