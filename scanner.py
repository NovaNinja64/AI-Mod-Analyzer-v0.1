import os
import sys
import glob
import winreg
from pathlib import Path

GAME_NAME = "Skyrim Special Edition"
APPDATA = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
ROAMING = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming"))

def _registry_paths():
    found = []
    keys = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Bethesda Softworks\Skyrim Special Edition"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Bethesda Softworks\Skyrim Special Edition"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Bethesda Softworks\Skyrim Special Edition"),
    ]
    for hive, key in keys:
        try:
            with winreg.OpenKey(hive, key) as h:
                value, _ = winreg.QueryValueEx(h, "Installed Path")
                p = Path(value)
                if p.exists():
                    found.append(p)
        except OSError:
            pass
    return found

def _steam_libraries():
    libs = []
    candidates = [
        Path("C:/Program Files (x86)/Steam/steamapps/common"),
        Path("C:/Program Files/Steam/steamapps/common"),
        Path("D:/SteamLibrary/steamapps/common"),
        Path("D:/Steam/steamapps/common"),
    ]
    steam_roots = [Path("C:/Program Files (x86)/Steam"), Path("C:/Program Files/Steam"), Path("D:/SteamLibrary")]
    for root in steam_roots:
        vdf = root / "steamapps/libraryfolders.vdf"
        if vdf.exists():
            try:
                import re
                for raw in re.findall(r'"path"\s+"([^"]+)"', vdf.read_text(encoding="utf-8", errors="ignore")):
                    libs.append(Path(raw.replace("\\\\", "\\")) / "steamapps/common")
            except OSError:
                pass
    return candidates + libs

def _valid_game(path):
    return path.exists() and (path / "SkyrimSE.exe").exists()

def scan_skyrim():
    candidates = _registry_paths() + [p / GAME_NAME for p in _steam_libraries()]
    unique = []
    seen = set()
    for p in candidates:
        key = str(p).lower()
        if key not in seen:
            seen.add(key); unique.append(p)
    game = next((p for p in unique if _valid_game(p)), None)
    plugins_file = APPDATA / "Skyrim Special Edition/plugins.txt"
    loadorder_file = APPDATA / "Skyrim Special Edition/loadorder.txt"
    plugins = []
    if plugins_file.exists():
        try:
            plugins = [line.strip().lstrip("*") for line in plugins_file.read_text(encoding="utf-8-sig", errors="ignore").splitlines()
                       if line.strip() and not line.strip().startswith("#")]
        except OSError:
            pass
    data = game / "Data" if game else None
    file_count = 0
    if data and data.exists():
        try:
            file_count = sum(1 for p in data.rglob("*") if p.is_file())
        except (OSError, PermissionError):
            pass
    return {
        "found": bool(game), "path": str(game) if game else None,
        "data_path": str(data) if data and data.exists() else None,
        "plugins_file": str(plugins_file) if plugins_file.exists() else None,
        "loadorder_file": str(loadorder_file) if loadorder_file.exists() else None,
        "plugins": plugins, "data_file_count": file_count
    }

def scan_system():
    managers = []
    vortex_candidates = [
        ROAMING / "Vortex", APPDATA / "Programs/Vortex",
        Path("C:/Program Files/Black Tree Gaming Ltd/Vortex")
    ]
    vortex = next((p for p in vortex_candidates if p.exists()), None)
    managers.append({"name":"Vortex","found":bool(vortex),"path":str(vortex) if vortex else None})
    mo2_candidates = [
        Path("C:/Modding/ModOrganizer"), Path("C:/ModOrganizer"),
        Path("C:/Program Files/Mod Organizer 2"),
        Path.home() / "Modding/ModOrganizer"
    ]
    mo2 = next((p for p in mo2_candidates if p.exists() and (p / "ModOrganizer.exe").exists()), None)
    # Also inspect common portable instances by searching a limited set of likely roots.
    if not mo2:
        for base in [Path("C:/Modding"), Path("D:/Modding"), Path.home() / "Games"]:
            if base.exists():
                try:
                    mo2 = next((p for p in base.glob("**/ModOrganizer.exe") if len(p.parts) < 8), None)
                except (OSError, PermissionError):
                    pass
            if mo2: break
    managers.append({"name":"Mod Organizer 2","found":bool(mo2),"path":str(mo2) if mo2 else None})
    return {"windows": "Windows" if os.name == "nt" else sys.platform, "managers": managers}
