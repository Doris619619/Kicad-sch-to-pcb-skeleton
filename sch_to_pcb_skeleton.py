from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class Component:
    ref: str
    value: str
    footprint: str
    fields: Dict[str, str] = field(default_factory=dict)


@dataclass
class NetNode:
    ref: str
    pin: str


@dataclass
class Net:
    code: int
    name: str
    nodes: List[NetNode] = field(default_factory=list)


class NetlistError(RuntimeError):
    pass


class FootprintLoadError(RuntimeError):
    pass


# --------------------------
# Netlist export / parse
# --------------------------
def run_kicad_cli_export_netlist(kicad_cli: str, sch_path: Path, net_path: Path) -> None:
    cmd = [
        kicad_cli,
        "sch",
        "export",
        "netlist",
        "--format",
        "kicadxml",
        str(sch_path),
        "-o",
        str(net_path),
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            "Failed to export netlist.\n"
            f"Command: {' '.join(cmd)}\n"
            f"stdout:\n{proc.stdout}\n"
            f"stderr:\n{proc.stderr}"
        )


def parse_netlist(net_path: Path) -> Tuple[List[Component], List[Net]]:
    try:
        raw = net_path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        raw = ""

    if raw.lstrip().startswith("("):
        raise NetlistError(
            "Exported netlist appears to be S-expression, not XML. "
            "Please ensure the export command used --format kicadxml."
        )

    try:
        tree = ET.parse(net_path)
    except ET.ParseError as exc:
        preview = raw[:200].replace("\n", " ") if raw else "<empty file>"
        raise NetlistError(f"Cannot parse netlist XML: {exc}. File start preview: {preview}") from exc

    root = tree.getroot()
    components_el = root.find("./components")
    nets_el = root.find("./nets")

    if components_el is None:
        raise NetlistError("No <components> node in netlist.")

    components: List[Component] = []
    for comp_el in components_el.findall("./comp"):
        ref = comp_el.get("ref", "").strip()
        value = (comp_el.findtext("value") or "").strip()
        footprint = (comp_el.findtext("footprint") or "").strip()

        fields: Dict[str, str] = {}
        for field_el in comp_el.findall("./fields/field"):
            name = (field_el.get("name") or "").strip()
            if name:
                fields[name] = (field_el.text or "").strip()
        for prop_el in comp_el.findall("./property"):
            name = (prop_el.get("name") or "").strip()
            value_prop = (prop_el.get("value") or "").strip()
            if name and name not in fields:
                fields[name] = value_prop

        if not ref:
            continue

        components.append(Component(ref=ref, value=value, footprint=footprint, fields=fields))

    nets: List[Net] = []
    if nets_el is not None:
        for net_el in nets_el.findall("./net"):
            try:
                code = int(net_el.get("code", "-1"))
            except ValueError:
                code = -1
            name = (net_el.get("name") or "").strip()
            nodes: List[NetNode] = []
            for node_el in net_el.findall("./node"):
                ref = (node_el.get("ref") or "").strip()
                pin = (node_el.get("pin") or "").strip()
                if ref and pin:
                    nodes.append(NetNode(ref=ref, pin=pin))
            nets.append(Net(code=code, name=name, nodes=nodes))

    return components, nets


# --------------------------
# Footprint library resolving
# --------------------------
def split_footprint_id(fp_id: str) -> Tuple[str, str]:
    if ":" not in fp_id:
        raise FootprintLoadError(
            f"Footprint identifier '{fp_id}' is not in 'library:name' format. "
            "The script cannot automatically load it."
        )
    lib_nickname, footprint_name = fp_id.split(":", 1)
    lib_nickname = lib_nickname.strip()
    footprint_name = footprint_name.strip()
    if not lib_nickname or not footprint_name:
        raise FootprintLoadError(f"Footprint identifier '{fp_id}' is incomplete.")
    return lib_nickname, footprint_name


def kicad_root_from_cli(kicad_cli: str) -> Optional[Path]:
    try:
        cli_path = Path(kicad_cli).resolve()
    except Exception:
        return None
    # .../KiCad/9.0/bin/kicad-cli.exe -> .../KiCad/9.0
    try:
        return cli_path.parent.parent
    except Exception:
        return None


def infer_standard_footprint_dir(kicad_root: Optional[Path]) -> Optional[Path]:
    if not kicad_root:
        return None
    candidate = kicad_root / "share" / "kicad" / "footprints"
    return candidate if candidate.exists() else None


def ensure_kicad_path_vars(kicad_root: Optional[Path]) -> None:
    std_fp = infer_standard_footprint_dir(kicad_root)
    if not std_fp:
        return
    # Set fallbacks for common version variables, in case the library table references old variables.
    for var in [
        "KICAD9_FOOTPRINT_DIR",
        "KICAD8_FOOTPRINT_DIR",
        "KICAD7_FOOTPRINT_DIR",
        "KICAD6_FOOTPRINT_DIR",
        "KISYSMOD",
    ]:
        os.environ.setdefault(var, str(std_fp))


def candidate_global_fp_lib_tables() -> List[Path]:
    cands: List[Path] = []
    appdata = os.environ.get("APPDATA")
    if appdata:
        cands.extend(
            [
                Path(appdata) / "kicad" / "9.0" / "fp-lib-table",
                Path(appdata) / "kicad" / "fp-lib-table",
                Path(appdata) / "KiCad" / "9.0" / "fp-lib-table",
                Path(appdata) / "KiCad" / "fp-lib-table",
            ]
        )
    home = Path.home()
    cands.extend(
        [
            home / "AppData" / "Roaming" / "kicad" / "9.0" / "fp-lib-table",
            home / "AppData" / "Roaming" / "kicad" / "fp-lib-table",
            home / ".config" / "kicad" / "9.0" / "fp-lib-table",
            home / ".config" / "kicad" / "fp-lib-table",
        ]
    )
    seen = set()
    out: List[Path] = []
    for p in cands:
        s = str(p)
        if s not in seen:
            seen.add(s)
            out.append(p)
    return out


def extract_balanced_blocks(text: str, head: str) -> List[str]:
    blocks: List[str] = []
    i = 0
    n = len(text)
    while i < n:
        idx = text.find(head, i)
        if idx == -1:
            break
        depth = 0
        in_str = False
        esc = False
        start = idx
        j = idx
        while j < n:
            ch = text[j]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
            else:
                if ch == '"':
                    in_str = True
                elif ch == '(':
                    depth += 1
                elif ch == ')':
                    depth -= 1
                    if depth == 0:
                        blocks.append(text[start : j + 1])
                        i = j + 1
                        break
            j += 1
        else:
            break
    return blocks


def parse_fp_lib_table(table_path: Path) -> Dict[str, str]:
    text = table_path.read_text(encoding="utf-8", errors="replace")
    blocks = extract_balanced_blocks(text, "(lib")
    mapping: Dict[str, str] = {}
    for block in blocks:
        m_name = re.search(r'\(name\s+"([^"]+)"\)', block, flags=re.DOTALL)
        m_uri = re.search(r'\(uri\s+"([^"]+)"\)', block, flags=re.DOTALL)
        if m_name and m_uri:
            mapping[m_name.group(1).strip()] = m_uri.group(1).strip()
    return mapping


def expand_kicad_vars(uri: str, project_dir: Path, kicad_root: Optional[Path]) -> str:
    ensure_kicad_path_vars(kicad_root)
    result = uri.replace("${KIPRJMOD}", str(project_dir))

    def repl(match: re.Match[str]) -> str:
        var = match.group(1)
        if var == "KIPRJMOD":
            return str(project_dir)
        value = os.environ.get(var)
        if value:
            return value
        return match.group(0)

    result = re.sub(r"\$\{([^}]+)\}", repl, result)
    return result


def build_library_map(project_dir: Path, kicad_root: Optional[Path]) -> Dict[str, Path]:
    mapping: Dict[str, Path] = {}

    # Read global tables first, then project; project table should override same nicknames.
    for table in candidate_global_fp_lib_tables():
        if table.exists():
            try:
                for name, uri in parse_fp_lib_table(table).items():
                    mapping[name] = Path(expand_kicad_vars(uri, project_dir, kicad_root)).resolve()
            except Exception:
                pass

    project_table = project_dir / "fp-lib-table"
    if project_table.exists():
        try:
            for name, uri in parse_fp_lib_table(project_table).items():
                mapping[name] = Path(expand_kicad_vars(uri, project_dir, kicad_root)).resolve()
        except Exception:
            pass

    # Finally, provide a strong fallback for standard libraries: nickname -> <standard_dir>/<nickname>.pretty
    std_fp = infer_standard_footprint_dir(kicad_root)
    if std_fp:
        for pretty_dir in std_fp.glob("*.pretty"):
            nickname = pretty_dir.stem
            mapping.setdefault(nickname, pretty_dir.resolve())

    return mapping


def resolve_library_path(lib_nickname: str, library_map: Dict[str, Path]) -> Path:
    lib_path = library_map.get(lib_nickname)
    if lib_path is None:
        raise FootprintLoadError(
            f"Cannot find library path for footprint library nickname '{lib_nickname}'. "
            "Please check global/project fp-lib-table, or confirm that the library is a standard one."
        )
    return lib_path


# --------------------------
# PCB generation
# --------------------------
def load_footprint(pcbnew, io_plugin, library_map: Dict[str, Path], footprint_id: str):
    lib_nickname, footprint_name = split_footprint_id(footprint_id)
    lib_path = resolve_library_path(lib_nickname, library_map)

    # According to Doxygen, PCB_IO.FootprintLoad's first parameter is aLibraryPath, not nickname.
    fp = io_plugin.FootprintLoad(str(lib_path), footprint_name)
    if fp is None:
        raise FootprintLoadError(
            f"Unable to load footprint '{footprint_name}' from library path '{lib_path}'."
        )
    return fp


def grid_position_mm(index: int, columns: int, pitch_x_mm: float, pitch_y_mm: float, margin_mm: float) -> Tuple[float, float]:
    row, col = divmod(index, columns)
    x_mm = margin_mm + col * pitch_x_mm
    y_mm = margin_mm + row * pitch_y_mm
    return x_mm, y_mm


def assign_nets_to_footprint(pcbnew, footprint, comp_ref: str, comp_to_nodes: Dict[str, List[Tuple[str, str]]], net_items: Dict[str, object], warnings: List[str]) -> None:
    for pin_number, net_name in comp_to_nodes.get(comp_ref, []):
        net_item = net_items.get(net_name)
        if net_item is None:
            continue
        pad = footprint.FindPadByNumber(pin_number)
        if pad is None:
            warnings.append(f"Pad '{pin_number}' not found in footprint for {comp_ref}, cannot assign to net '{net_name}'.")
            continue
        pad.SetNet(net_item)


def build_board_from_netlist(
    output_pcb: Path,
    project_dir: Path,
    kicad_cli: str,
    components: List[Component],
    nets: List[Net],
    columns: int,
    pitch_x_mm: float,
    pitch_y_mm: float,
    margin_mm: float,
    copper_layers: int,
) -> Tuple[int, int, List[str], List[str]]:
    try:
        import pcbnew  # type: ignore
    except Exception as exc:
        raise RuntimeError(
            "Current Python environment cannot import pcbnew.\n"
            "This step must be run with a Python interpreter that can import the KiCad pcbnew module."
        ) from exc

    board = pcbnew.BOARD()
    board.SetFileName(str(output_pcb))
    if hasattr(board, "SetGenerator"):
        board.SetGenerator("sch_to_pcb_skeleton.py")
    if hasattr(board, "SetCopperLayerCount"):
        board.SetCopperLayerCount(max(1, copper_layers))

    kicad_root = kicad_root_from_cli(kicad_cli)
    library_map = build_library_map(project_dir, kicad_root)

    warnings: List[str] = []
    errors: List[str] = []

    # Explicitly instantiate KiCad s-expression footprint IO to avoid relying on global nickname resolver.
    io_plugin = pcbnew.PCB_IO_KICAD_SEXPR()

    # Create net objects first. Skip empty net names.
    net_items: Dict[str, object] = {}
    for net in nets:
        if not net.name:
            continue
        try:
            net_item = board.FindNet(net.name)
        except Exception:
            net_item = None

        if net_item is None:
            net_item = pcbnew.NETINFO_ITEM(board, net.name)
            board.AddNative(net_item)
        net_items[net.name] = net_item

    comp_to_nodes: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
    for net in nets:
        if not net.name:
            continue
        for node in net.nodes:
            comp_to_nodes[node.ref].append((node.pin, net.name))

    added = 0
    skipped = 0

    for index, comp in enumerate(components):
        if not comp.footprint:
            skipped += 1
            warnings.append(f"{comp.ref} has no footprint, skipped.")
            continue

        try:
            fp = load_footprint(pcbnew, io_plugin, library_map, comp.footprint)
        except Exception as exc:
            skipped += 1
            errors.append(f"{comp.ref}: {exc}")
            continue

        fp.SetReference(comp.ref)
        fp.SetValue(comp.value or comp.ref)
        if hasattr(fp, "SetFPIDAsString"):
            try:
                fp.SetFPIDAsString(comp.footprint)
            except Exception:
                pass

        x_mm, y_mm = grid_position_mm(index, columns, pitch_x_mm, pitch_y_mm, margin_mm)
        pos = pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm))
        fp.SetPosition(pos)
        if hasattr(fp, "SetNeedsPlaced"):
            fp.SetNeedsPlaced(True)
        if hasattr(fp, "SetIsPlaced"):
            fp.SetIsPlaced(False)

        board.AddNative(fp)
        assign_nets_to_footprint(pcbnew, fp, comp.ref, comp_to_nodes, net_items, warnings)
        added += 1

    try:
        board.BuildConnectivity()
    except Exception:
        pass

    pcbnew.PCB_IO_MGR.Save(pcbnew.PCB_IO_MGR.KICAD_SEXP, str(output_pcb), board)
    return added, skipped, warnings, errors


# --------------------------
# CLI
# --------------------------
def locate_default_output_paths(sch_path: Path) -> Tuple[Path, Path]:
    base = sch_path.with_suffix("")
    return base.with_suffix(".net"), base.with_suffix(".kicad_pcb")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate initial PCB skeleton from KiCad schematic (standalone script)")
    parser.add_argument("--sch", required=True, help="Input .kicad_sch path")
    parser.add_argument("--out", help="Output .kicad_pcb path; defaults to same basename as schematic")
    parser.add_argument("--net", help="Intermediate netlist path; defaults to same basename as schematic")
    parser.add_argument("--kicad-cli", default="kicad-cli", help="kicad-cli executable path, default looks up from PATH")
    parser.add_argument("--columns", type=int, default=8, help="Number of components per row, default 8")
    parser.add_argument("--pitch-x", type=float, default=25.0, help="X spacing between adjacent components (mm), default 25")
    parser.add_argument("--pitch-y", type=float, default=20.0, help="Y spacing between adjacent components (mm), default 20")
    parser.add_argument("--margin", type=float, default=20.0, help="Top-left margin (mm), default 20")
    parser.add_argument("--copper-layers", type=int, default=2, help="Number of copper layers, default 2")
    parser.add_argument("--keep-net", action="store_true", help="Keep the exported netlist file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    sch_path = Path(args.sch).resolve()
    if not sch_path.exists():
        print(f"[Error] Schematic does not exist: {sch_path}", file=sys.stderr)
        return 1

    project_dir = sch_path.parent

    default_net, default_out = locate_default_output_paths(sch_path)
    net_path = Path(args.net).resolve() if args.net else default_net
    out_path = Path(args.out).resolve() if args.out else default_out

    out_path.parent.mkdir(parents=True, exist_ok=True)
    net_path.parent.mkdir(parents=True, exist_ok=True)

    temp_net = False
    if not args.keep_net and not args.net:
        fd, temp_name = tempfile.mkstemp(suffix=".net")
        os.close(fd)
        net_path = Path(temp_name)
        temp_net = True

    print(f"[1/4] Exporting netlist: {sch_path} -> {net_path}")
    run_kicad_cli_export_netlist(args.kicad_cli, sch_path, net_path)

    print(f"[2/4] Parsing netlist: {net_path}")
    components, nets = parse_netlist(net_path)
    print(f"      Components: {len(components)}, nets: {len(nets)}")

    print(f"[3/4] Generating initial PCB skeleton: {out_path}")
    added, skipped, warnings, errors = build_board_from_netlist(
        output_pcb=out_path,
        project_dir=project_dir,
        kicad_cli=args.kicad_cli,
        components=components,
        nets=nets,
        columns=max(1, args.columns),
        pitch_x_mm=args.pitch_x,
        pitch_y_mm=args.pitch_y,
        margin_mm=args.margin,
        copper_layers=args.copper_layers,
    )

    print("[4/4] Done")
    print(f"      Footprints successfully imported: {added}")
    print(f"      Skipped components: {skipped}")
    print(f"      Output PCB: {out_path}")

    if warnings:
        print("\n[Warnings]")
        for item in warnings:
            print(f"  - {item}")

    if errors:
        print("\n[Errors: these components were not added to the PCB]")
        for item in errors:
            print(f"  - {item}")

    if temp_net:
        try:
            net_path.unlink(missing_ok=True)
        except Exception:
            pass

    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
