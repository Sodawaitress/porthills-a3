# -*- coding: utf-8 -*-
"""ERST619 A3 -- Map 3 (spatial data cleaning).

Companion to 44_build_all_maps.py: same page geometry, fonts, north arrow,
scale bar and AOI extent, so all three maps read as one set
(map_making_guide.md §4/§5/§6). Adds to PortHills2017.aprx:

  Map 3  Map3_DataCleaning   the per-cell cleaning flag behind
                             figures/A3_0_spatial_cleaning_funnel.png

Only this layout / its map is deleted and rebuilt; Map 1/2 are
untouched. Run with ArcGIS Pro CLOSED:
  "C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe" 45_build_cleaning_map.py
"""
import os, arcpy

BASE  = r"C:\Users\zhouy3d\Desktop\PortHills"
APRX  = BASE + r"\PortHills2017\PortHills2017.aprx"
GDB   = BASE + r"\PortHills2017\PortHills2017.gdb"
PERIM = BASE + r"\data\Port_Hills_2017_Fire_Boundary.shp"
EXT_REF = os.path.join(GDB, "FuelClass_SSp_masked")      # Map 1's AOI extent
OUT   = r"C:\Users\zhouy3d\Desktop\a3\exploration\map_variants"

# cleaning_mask was built on the school machine in 2017PortHillsA3.gdb
# (values 1-5, see CLEAN_CLASSES); it is copied into the main gdb once
CLEAN_SRC = (r"C:\Users\zhouy3d\OneDrive - Lincoln University\Lincoln University"
             r"\ERST619\PortHills\PortHills2017\2017PortHillsA3.gdb\cleaning_mask")
CLEAN = os.path.join(GDB, "Cleaning_Mask_2017")

BASEMAP = "NZ Light Grey Canvas (Vector)"
FONT = "Calibri"
SZ_TITLE, SZ_LEGHEAD, SZ_LEGLABEL, SZ_CRED = 22, 11, 9, 7
PAGE_MID = 148.5
MARGIN = 12
MAIN = (12, 32, 212, 180)
RIGHT_X, RIGHT_X2 = 220, 285
TITLE_Y, CRED_Y = 198, 27
N_NARROW_Y, NARROW_H, N_LEGEND_Y, R_SCALE_Y = 176, 13, 156, 30
CELL_HA = 0.09                                           # 30 m x 30 m

os.makedirs(OUT, exist_ok=True)
arcpy.env.overwriteOutput = True


def h2r(h):
    return [int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), 100]


# value -> (label, hex). Retained cells pale, removed/flagged cells strong,
# so the eye goes to what cleaning took out. Okabe-Ito hues for the flags.
CLEAN_CLASSES = {
    1: ("Kept: 23 Jan 2017 image",            "#ece6d6"),
    5: ("Kept: gap-filled, 16 Jan 2017",      "#cdb88a"),
    2: ("Removed: mixed edge cell",           "#e69f00"),
    3: ("Removed from dNBR: cloud gap",       "#56b4e9"),
    4: ("Flagged, kept: negative reflectance", "#7a0177"),
}
CLEAN_ORDER = [1, 5, 2, 3, 4]

p = arcpy.mp.ArcGISProject(APRX)


def cimobj(n):
    return arcpy.cim.CreateCIMObjectFromClassName(n, 'V3')


def rgb(v):
    c = cimobj('CIMRGBColor')
    c.values = v
    return c


def restyle(symref, size, bold=False):
    try:
        s = symref.symbol
        s.height = size
        s.fontFamilyName = FONT
        s.fontStyleName = "Bold" if bold else "Regular"
    except Exception as e:
        print("   restyle skipped:", e)


def strip_attribution(m):
    try:
        md = m.getDefinition('V3')
        if getattr(md, 'attribution', ''):
            md.attribution = ''
            m.setDefinition(md)
    except Exception:
        pass
    for l in m.listLayers():
        try:
            d = l.getDefinition('V3')
            if getattr(d, 'attribution', ''):
                d.attribution = ''
                l.setDefinition(d)
        except Exception:
            pass


def hollow(lyr, w=1.6):
    s = lyr.symbology
    s.renderer.symbol.color = {'RGB': [0, 0, 0, 0]}
    s.renderer.symbol.outlineColor = {'RGB': [0, 0, 0, 100]}
    s.renderer.symbol.outlineWidth = w
    lyr.symbology = s


def new_map(name):
    for m in p.listMaps(name):
        p.deleteItem(m)
    m = p.createMap(name, "Map")
    m.spatialReference = arcpy.SpatialReference(2193)
    m.addBasemap(BASEMAP)
    return m


def add_perimeter(m, w=1.6):
    per = m.addDataFromPath(PERIM)
    per.name = "2017 fire perimeter"
    hollow(per, w)
    return per


def txt(lo, x, y, s, size, name, bold=False):
    e = p.createTextElement(lo, arcpy.Point(x, y), "POINT", s, size, FONT,
                            "Bold" if bold else "Regular", None, name)
    e.setAnchor("TOP_LEFT_CORNER")
    e.elementPositionX = x
    e.elementPositionY = y
    return e


# ---- shared AOI extent: identical maths to 44_build_all_maps.py ------------
ex = arcpy.Describe(EXT_REF).extent
pad = 0.04 * max(ex.width, ex.height)
_h = ex.height + 2 * pad
_w = _h * ((MAIN[2] - MAIN[0]) / (MAIN[3] - MAIN[1]))
EXT = arcpy.Extent(ex.XMin - pad, ex.YMin - pad, ex.XMin - pad + _w, ex.YMax + pad,
                   spatial_reference=arcpy.SpatialReference(2193))

CRED_CRS = "Projection: NZGD2000 / New Zealand Transverse Mercator 2000 (EPSG:2193)."
CRED_SIG = "Y. Zhou, ERST619, 26 September 2026."
NO_LOC = "Locator inset is shown on Map 1 only and is not repeated here."


def build_layout(lname, title, m, legend_layers, credits):
    """Same frame / N arrow / legend / scale bar positions as Map 2."""
    for lo in p.listLayouts(lname):
        p.deleteItem(lo)
    lo = p.copyItem(p.listLayouts("Layout1")[0], lname) or p.listLayouts(lname)[0]
    for e in lo.listElements("TEXT_ELEMENT"):
        lo.deleteElement(e)

    mf = lo.listElements("MAPFRAME_ELEMENT")[0]
    mf.setAnchor("BOTTOM_LEFT_CORNER")
    mf.elementPositionX, mf.elementPositionY = MAIN[0], MAIN[1]
    mf.elementWidth = MAIN[2] - MAIN[0]
    mf.elementHeight = MAIN[3] - MAIN[1]
    mf.map = m
    mf.camera.setExtent(EXT)

    t = txt(lo, MARGIN, TITLE_Y, title, SZ_TITLE, "Title", bold=True)
    td = t.getDefinition('V3')
    try:
        td.graphic.symbol.symbol.horizontalAlignment = 'Center'
        t.setDefinition(td)
    except Exception as e:
        print("   title align skipped:", e)
    t.setAnchor("TOP_MID_POINT")
    t.elementPositionX = PAGE_MID
    t.elementPositionY = TITLE_Y

    na = lo.listElements("MAPSURROUND_ELEMENT", "North Arrow")[0]
    na.setAnchor("TOP_LEFT_CORNER")
    na.elementWidth = na.elementHeight = NARROW_H
    na.elementPositionX, na.elementPositionY = RIGHT_X, N_NARROW_Y

    lg = lo.listElements("LEGEND_ELEMENT")[0]
    lg.syncNewLayer = False
    lg.syncLayerOrder = False
    for it in list(lg.items):
        lg.removeItem(it)
    for l in legend_layers:
        lg.addItem(l)
    d = lg.getDefinition('V3')
    d.autoFonts = False
    d.columns = 1
    d.fittingStrategy = 'AdjustFrame'
    for i in d.items:
        if getattr(i, 'name', '') == "2017 fire perimeter":
            i.showLayerName = False
        restyle(i.labelSymbol, SZ_LEGLABEL)
        restyle(i.layerNameSymbol, SZ_LEGHEAD, bold=True)
        restyle(i.headingSymbol, SZ_LEGLABEL, bold=True)
    lg.setDefinition(d)
    lg.setAnchor("TOP_LEFT_CORNER")
    lg.elementPositionX, lg.elementPositionY = RIGHT_X, N_LEGEND_Y
    lg.elementWidth = RIGHT_X2 - RIGHT_X

    sb = lo.listElements("MAPSURROUND_ELEMENT", "Scale Bar")[0]
    sd = sb.getDefinition('V3')
    sd.fittingStrategy = 'AdjustFrame'
    sd.division, sd.divisions, sd.subdivisions = 1.0, 2, 2
    sd.labelFrequency = 'Divisions'
    restyle(sd.labelSymbol, SZ_LEGLABEL)
    restyle(sd.unitLabelSymbol, SZ_LEGLABEL)
    sb.setDefinition(sd)
    sb.setAnchor("BOTTOM_LEFT_CORNER")
    sb.elementPositionX, sb.elementPositionY = RIGHT_X, R_SCALE_Y

    txt(lo, MARGIN, CRED_Y, "\n".join(credits), SZ_CRED, "Credits")
    lo.exportToPNG(os.path.join(OUT, lname + ".png"), resolution=150)
    lo.exportToPDF(os.path.join(OUT, lname + ".pdf"), resolution=300)
    print("  ok", lname)


# ============================ Map 3: cleaning ===============================
if not arcpy.Exists(CLEAN):
    arcpy.management.CopyRaster(CLEAN_SRC, CLEAN)
    arcpy.management.BuildRasterAttributeTable(CLEAN, "Overwrite")
if "ClassName" not in [f.name for f in arcpy.ListFields(CLEAN)]:
    arcpy.management.AddField(CLEAN, "ClassName", "TEXT", field_length=80)

counts = {}
with arcpy.da.UpdateCursor(CLEAN, ["Value", "Count", "ClassName"]) as cur:
    for v, n, _ in cur:
        v = int(v)
        if v in CLEAN_CLASSES:
            counts[v] = n
            cur.updateRow([v, n, "%s (%s ha)" % (CLEAN_CLASSES[v][0],
                                                format(n * CELL_HA, ",.1f"))])
for v in CLEAN_ORDER:
    print("  cleaning class %d: %6d cells = %7.2f ha" % (v, counts.get(v, 0),
                                                        counts.get(v, 0) * CELL_HA))

m3 = new_map("Map_Map3_DataCleaning")
c3 = m3.addDataFromPath(CLEAN)
c3.name = "Cleaning flag (30 m cell)"
s = c3.symbology
if s.colorizer.type != 'RasterUniqueValueColorizer':
    s.updateColorizer('RasterUniqueValueColorizer')
s.colorizer.field = "ClassName"
c3.symbology = s
d = c3.getDefinition('V3')
for g in d.colorizer.groups:
    for it in g.classes:
        v = next((k for k, (lab, _) in CLEAN_CLASSES.items() if it.label.startswith(lab)), None)
        if v is not None:
            it.color = rgb(h2r(CLEAN_CLASSES[v][1]))
    g.classes = sorted(g.classes, key=lambda i: next(
        (CLEAN_ORDER.index(k) for k, (lab, _) in CLEAN_CLASSES.items()
         if i.label.startswith(lab)), 99))
    g.heading = ''
d.colorizer.noDataColor = rgb([255, 255, 255, 0])
c3.setDefinition(d)
p3 = add_perimeter(m3, 0.5)      # thin, or it hides the mixed-edge ring
strip_attribution(m3)

build_layout(
    "Map3_DataCleaning",
    "Map 3: Spatial data cleaning of the 30 m grid, Port Hills fire, 2017",
    m3, [c3, p3],
    ["Data: Landsat 8 OLI Collection 2 Level-2 (USGS); CDEM/ECan 2017 fire boundary. "
     "Basemap: Eagle Technology, LINZ, StatsNZ, NIWA.",
     "Mixed edge cells straddle the perimeter and are dropped from every analysis. "
     "Cloud-gap cells have no post-fire value, so they leave",
     "the dNBR/refugia analysis only; the classification uses pre-fire imagery and keeps them. "
     "Negative-reflectance cells are the darkest",
     "char, so they are flagged rather than deleted. " + NO_LOC,
     CRED_CRS, CRED_SIG])

p.save()
print("saved")
