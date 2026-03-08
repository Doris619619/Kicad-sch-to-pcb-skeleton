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




## Dependencies

- KiCad 9 (with `kicad-cli` and the bundled Python environment)
- Python 3 (the KiCad‑bundled Python is recommended)

No additional Python packages are required – the script uses only the standard library and KiCad’s `pcbnew` module.

---

## Installation

1. Clone this repository or download `generate_pcb_skeleton.py` (or whatever the script is named, e.g., `sch_to_pcb_skeleton.py`).
2. Ensure you have KiCad 9 installed and note the paths to:
   - KiCad's bundled Python interpreter
   - `kicad-cli` executable

---

## Usage

### Command‑line arguments

| Argument        | Description                                                                 |
|-----------------|-----------------------------------------------------------------------------|
| `--sch`         | Path to the input KiCad schematic (`.kicad_sch`).                           |
| `--out`         | Path where the output PCB skeleton (`.kicad_pcb`) will be saved.            |
| `--kicad-cli`   | Full path to the `kicad-cli` executable (e.g. `kicad-cli.exe` on Windows). |
| `--keep-net`    | *(Optional)* Preserve the netlist after use (for debugging).                |
| `--help`        | Show help message and exit.                                                 |

### Basic command (Windows)

Open a Command Prompt and run:

```cmd
"<KICAD9_PYTHON>" "<PATH_TO_SCRIPT>\sch_to_pcb_skeleton.py" ^
    --sch "<PATH_TO_SCH>\my_design.kicad_sch" ^
    --out "<PATH_TO_OUTPUT>\my_design.kicad_pcb" ^
    --kicad-cli "<KICAD9_CLI>\kicad-cli.exe"
```

Replace the placeholders with your actual paths:

- `<KICAD9_PYTHON>` – e.g. `D:\app\KiCad\9.0\bin\python.exe`
- `<PATH_TO_SCRIPT>` – where you saved the script
- `<PATH_TO_SCH>` – folder containing your schematic
- `<PATH_TO_OUTPUT>` – folder where the PCB file will be created
- `<KICAD9_CLI>` – e.g. `D:\app\KiCad\9.0\bin\kicad-cli.exe`

### Example (Windows)

Here is a concrete example from a real setup:

```cmd
D:\>"D:\app\KiCad\9.0\bin\python.exe" "D:\kicad_test\tools\sch_to_pcb_skeleton.py" --sch "D:\kicad_test\case3\case3.kicad_sch" --out "D:\kicad_test\case3\case3_skeleton.kicad_pcb" --kicad-cli "D:\app\KiCad\9.0\bin\kicad-cli.exe" --keep-net
```

This command:

- Uses the KiCad 9 Python interpreter.
- Runs the script located at `D:\kicad_test\tools\sch_to_pcb_skeleton.py`.
- Reads the schematic `D:\kicad_test\case3\case3.kicad_sch`.
- Outputs the PCB skeleton to `D:\kicad_test\case3\case3_skeleton.kicad_pcb`.
- Specifies the path to `kicad-cli.exe`.
- The `--keep-net` flag keeps the intermediate netlist file for debugging.

### Linux / macOS

On Unix‑like systems, adjust the paths and use the appropriate Python interpreter (KiCad’s bundled Python is typically installed under `/usr/bin` or a custom prefix). The `kicad-cli` executable is usually named `kicad-cli` (without `.exe`).

```bash
/path/to/kicad/bin/python generate_pcb_skeleton.py \
    --sch /home/user/design/board.kicad_sch \
    --out /home/user/design/board.kicad_pcb \
    --kicad-cli /path/to/kicad/bin/kicad-cli
```

---

## Output

The script produces a `.kicad_pcb` file that contains:

- All footprints from the schematic, placed in a simple initial layout (components are positioned in a rough grid; no routing is performed).
- All nets and connections as defined in the schematic.
- A default board outline (you will need to adjust it to your mechanical requirements).

This file can be opened directly in **PCB Editor** (`pcbnew`) for further manual refinement.

---

## Limitations & Notes

- The component placement is rudimentary – it is **not** intended to be production‑ready. You must manually reposition components, route traces, add pours, etc.
- The board outline is a placeholder; you must define the correct mechanical shape.
- The script relies on `kicad-cli` to export a netlist and then uses `pcbnew` to create a board from that netlist.
- Tested only with KiCad 9 on Windows. Future KiCad versions may require adjustments.
- The `--keep-net` flag leaves the intermediate netlist file in the output directory for debugging; otherwise it is deleted automatically.

---

## Contributing

Contributions are welcome! If you encounter a bug or have an idea for improvement, please open an issue or submit a pull request.

---

## License

This project is provided under the [MIT License](LICENSE). Feel free to use and modify it for your own projects.
```
