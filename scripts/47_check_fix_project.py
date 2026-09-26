# -*- coding: utf-8 -*-
"""One-click "why is my data missing" fixer for the PortHills project folder.

For every .aprx under ROOT, every layer is checked:
  ok        source exists AND lives inside ROOT (so the folder is self-contained)
  FIXED     source was missing or outside ROOT; a dataset with the same name
            was found inside ROOT and the layer was re-pointed to it
  BROKEN    nothing with that name exists inside ROOT -- the data really is
            missing and has to be copied in by hand (the report says the name)

Run with ArcGIS Pro CLOSED (Pro locks the .aprx):
  "C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe" 47_check_fix_project.py [ROOT]
ROOT defaults to the working copy on the Desktop; pass the OneDrive copy's
folder to check that one instead. Add --dry to only report, not change.
"""
import os, re, sys, arcpy

args = [a for a in sys.argv[1:] if not a.startswith("--")]
DRY = "--dry" in sys.argv
ROOT_RAW = os.path.abspath(args[0] if args else r"C:\Users\zhouy3d\Desktop\PortHills")
ROOT = os.path.normcase(ROOT_RAW)
SKIP_DIRS = {".backups", "_aprx_backups", "GpMessages", "ImportLog", "Index"}

# ---- index every dataset inside ROOT by (lower-case) name -------------------
files, gdb_items, aprxs = {}, {}, []
for d, subdirs, fs in os.walk(ROOT_RAW):
    if d.lower().endswith(".gdb"):
        arcpy.env.workspace = d
        for n in (arcpy.ListFeatureClasses() or []) + (arcpy.ListRasters() or []) + \
                 (arcpy.ListTables() or []):
            gdb_items.setdefault(n.lower(), []).append(d)
        subdirs[:] = []
        continue
    subdirs[:] = [s for s in subdirs if s not in SKIP_DIRS]
    for f in fs:
        files.setdefault(f.lower(), []).append(d)
        if f.lower().endswith(".aprx") and "backup" not in f.lower():
            aprxs.append(os.path.join(d, f))


def fix_function_layer(l):
    """Raster-function layers (Extract Bands, Calculator...) hide their source
    path inside an XML string, often as a relative '..\\data' that arcpy cannot
    resolve. Rewrite every workspace path in that XML to the absolute folder
    inside ROOT that holds the named raster. Returns the new folder or None."""
    d = l.getDefinition('V3')
    dc = getattr(d, 'dataConnection', None)
    x = getattr(dc, 'dataset', '') or ''
    if not x.startswith('<'):
        return None
    names = re.findall(r"<Name>([^<]+\.(?:tif|tiff|img|dat))</Name>", x, re.I)
    if not names:
        return None
    hits = files.get(names[0].lower())
    if not hits:
        return None
    new = hits[0]
    x = re.sub(r"(<PathName>)[^<]*(</PathName>)", lambda m: m.group(1) + new + m.group(2), x)
    x = re.sub(r"(Workspace = )[^;]*(;)", lambda m: m.group(1) + new + m.group(2), x)
    x = re.sub(r"(<Key>DATABASE</Key><Value xsi:type='xs:string'>)[^<]*(</Value>)",
               lambda m: m.group(1) + new + m.group(2), x)
    if not DRY:
        dc.dataset = x
        l.setDefinition(d)
    return new


def inside(path):
    return os.path.normcase(os.path.abspath(path)).startswith(ROOT)


def find_ws(ws, ds):
    """Workspace inside ROOT that holds a dataset called ds (gdb first)."""
    cands = gdb_items.get(ds.lower(), []) if ws.lower().endswith(".gdb") or "." not in ds \
        else files.get(ds.lower(), [])
    if not cands:
        cands = gdb_items.get(ds.lower(), []) + files.get(ds.lower(), [])
    if not cands:
        return None
    # prefer a workspace with the same folder/gdb name as the old one
    same = [c for c in cands if os.path.basename(c).lower() == os.path.basename(ws).lower()]
    return (same or cands)[0]


total_bad = 0
for ap in sorted(aprxs):
    print("\n==", os.path.relpath(ap, ROOT_RAW))
    p = arcpy.mp.ArcGISProject(ap)
    remap, changed = {}, False
    for m in p.listMaps():
        for l in m.listLayers():
            if l.isGroupLayer or getattr(l, "isBasemapLayer", False) or \
                    not l.supports("DATASOURCE"):
                continue
            src = l.dataSource
            if src.lower().startswith("http"):
                continue
            cp = l.connectionProperties or {}
            ws = (cp.get("connection_info") or {}).get("database", "")
            ds = cp.get("dataset", "") or os.path.basename(src)
            if not l.isBroken and arcpy.Exists(src) and inside(src):
                continue
            fn = fix_function_layer(l)
            if fn:
                changed = changed or not DRY
                status = "fixable" if DRY else ("FIXED" if not l.isBroken else "BROKEN")
                total_bad += status == "BROKEN"
                print("   %-7s %s / %s  (raster function)  ->  %s" % (status, m.name, l.name, fn))
                continue
            new_ws = find_ws(ws or os.path.dirname(src), ds)
            if new_ws and not DRY:
                try:
                    l.updateConnectionProperties(ws or os.path.dirname(src), new_ws)
                    remap[ws or os.path.dirname(src)] = new_ws
                    changed = True
                except Exception as e:
                    print("   update failed:", e)
            status = "FIXED" if new_ws and (DRY or not l.isBroken) else "BROKEN"
            if DRY and new_ws:
                status = "fixable"
            if status == "BROKEN":
                total_bad += 1
            print("   %-7s %s / %s  <-  %s%s" % (status, m.name, l.name, src,
                                             ("\n            now -> " + new_ws) if new_ws else ""))
    # raster-function layers keep their path inside XML; a project-wide remap
    # of the same folders catches those too
    for old, new in remap.items():
        try:
            p.updateConnectionProperties(old, new)
        except Exception:
            pass
    if changed and not DRY:
        try:
            p.save()
            print("   saved")
        except OSError:
            print("   !! could not save -- close ArcGIS Pro and run again")
print("\nstill missing:", total_bad, "layer(s)")
