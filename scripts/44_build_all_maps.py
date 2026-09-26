# -*- coding: utf-8 -*-
"""Canonical builder for the ERST619 A3 section-7 maps (4 marks).

Builds, inside PortHills2017.aprx, every Map + Layout for:
  Map 1  pre-fire fuel classes   (four variants, see SPECS_MAP1)
  Map 2  burn severity / refugia (one layout)

Layout follows map_making_guide.md:
  §4 lecturer's feedback  main map left; inset -> N arrow -> legend ->
                          scale bar stacked down a LEFT-ALIGNED right column
                          at x = RIGHT_X; 12 mm margins so nothing is clipped
  §1a A2 rubric           all six elements; where one is deliberately dropped
                          the reason is printed at the foot of the map
  §1b Helen's A1 notes    locator inset on Map 1 ONLY; north arrow identical
                          in style and position on every map
  §6  consistency         same frame, fonts (Calibri), scale bar, north arrow
                          and AOI extent across all maps

Everything is a real arcpy.mp object, so every element stays selectable and
movable in the ArcGIS Pro GUI.

Run with ArcGIS Pro CLOSED (aprx.save() raises OSError while Pro holds the
file lock).  Usage:
  "C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe" 44_build_all_maps.py
"""
import csv, os, arcpy

BASE  = r"C:\Users\zhouy3d\Desktop\PortHills"
APRX  = BASE + r"\PortHills2017\PortHills2017.aprx"
GDB   = BASE + r"\PortHills2017\PortHills2017.gdb"
SRC   = BASE + r"\data\R5_arcgis"
PERIM = BASE + r"\data\Port_Hills_2017_Fire_Boundary.shp"
CANT  = BASE + r"\data\CanterburyRegion.shp"
HS    = BASE + r"\PortHills2017\a3\raster\PortHills_HS1m_LiDAR.tif"
CLS   = os.path.join(GDB, "FuelClass_SSp_masked")
CONF  = os.path.join(GDB, "FuelClass_SSp_confidence")
SEV   = os.path.join(GDB, "Severity_2017_map_clipped")
OUT   = r"C:\Users\zhouy3d\Desktop\a3\exploration\map_variants"
BASEMAP = "NZ Light Grey Canvas (Vector)"
FONT = "Calibri"
os.makedirs(OUT, exist_ok=True)
arcpy.env.overwriteOutput = True

SZ_TITLE, SZ_LEGHEAD, SZ_LEGLABEL, SZ_CRED = 22, 11, 9, 7
PAGE_MID = 148.5

# ---- page geometry (mm, A4 landscape) -------------------------------------
MARGIN = 12
MAIN   = (12, 32, 212, 180)
RIGHT_X, RIGHT_X2 = 220, 285
FLOAT_INSET = (155, 123, 207, 175)   # panel floated inside the main map
TITLE_Y, CRED_Y = 198, 27

R_INSET = (RIGHT_X, 138, RIGHT_X2, 178)   # right column WITH a locator
R_NARROW_Y, NARROW_H = 128, 13
R_LEGEND_Y = 108
R_SCALE_Y = 30
N_NARROW_Y = 176                          # right column WITHOUT a locator
N_LEGEND_Y = 156

# ---- palettes --------------------------------------------------------------
rows  = list(csv.DictReader(open(os.path.join(SRC, "fuel_class_legend.csv"))))
FUEL_ORDER = [r["class"] for r in rows]


def h2r(h):
    return [int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), 100]


PAL_CSV = {r["class"]: h2r(r["hex"]) for r in rows}
PAL_CVD = dict(zip(FUEL_ORDER, [h2r(x) for x in
                                ("#f0e442", "#d55e00", "#009e73", "#0072b2", "#999999")]))
# guide §3: severity RdYlGn, unburned green -> high severity red
SEV_ORDER = ["Unburned (refugia)", "Low severity", "Moderate severity", "High severity"]
PAL_SEV = dict(zip(SEV_ORDER, [h2r(x) for x in
                               ("#1a9850", "#ffffbf", "#fdae61", "#d73027")]))

p = arcpy.mp.ArcGISProject(APRX)


def cimobj(n):
    return arcpy.cim.CreateCIMObjectFromClassName(n, 'V3')


def rgb(v):
    c = cimobj('CIMRGBColor')
    c.values = v
    return c


def poly(x0, y0, x1, y1):
    return arcpy.Polygon(arcpy.Array([arcpy.Point(x0, y0), arcpy.Point(x0, y1),
                                      arcpy.Point(x1, y1), arcpy.Point(x1, y0)]))


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


def set_palette(lyr, pal, field, order):
    """Unique-value colorizer with exact hex.

    arcpy's .color setter converts to CIMLABColor, which does not round-trip,
    so CIMRGBColor is written straight into the CIM instead.
    """
    s = lyr.symbology
    if s.colorizer.type != 'RasterUniqueValueColorizer':
        s.updateColorizer('RasterUniqueValueColorizer')
    s.colorizer.field = field
    lyr.symbology = s
    d = lyr.getDefinition('V3')
    for g in d.colorizer.groups:
        for it in g.classes:
            if it.label in pal:
                it.color = rgb(pal[it.label])
        g.classes = sorted(g.classes,
                           key=lambda i: order.index(i.label) if i.label in order else 99)
        g.heading = ''
    d.colorizer.noDataColor = rgb([255, 255, 255, 0])
    lyr.setDefinition(d)


def hollow(lyr, w=1.6):
    s = lyr.symbology
    s.renderer.symbol.color = {'RGB': [0, 0, 0, 0]}
    s.renderer.symbol.outlineColor = {'RGB': [0, 0, 0, 100]}
    s.renderer.symbol.outlineWidth = w
    lyr.symbology = s


def build_map(name, raster, pal, field, order, layer_name,
              hillshade=False, transparency=0):
    for m in p.listMaps(name):
        p.deleteItem(m)
    m = p.createMap(name, "Map")
    m.spatialReference = arcpy.SpatialReference(2193)
    m.addBasemap(BASEMAP)
    if hillshade:
        h = m.addDataFromPath(HS)
        h.name = "LiDAR hillshade"
        hsym = h.symbology
        if hsym.colorizer.type != 'RasterStretchColorizer':
            hsym.updateColorizer('RasterStretchColorizer')
        r = (p.listColorRamps('Black to White') or p.listColorRamps('White to Black')
             or p.listColorRamps('*Gray*'))
        if r:
            hsym.colorizer.colorRamp = r[0]
        h.symbology = hsym
        h.transparency = 35
    cls = m.addDataFromPath(raster)
    cls.name = layer_name
    set_palette(cls, pal, field, order)
    if transparency:
        cls.transparency = transparency
    per = m.addDataFromPath(PERIM)
    per.name = "2017 fire perimeter"
    hollow(per)
    strip_attribution(m)
    return m, cls, per


# ---- shared AOI extent (guide §6) -----------------------------------------
ex = arcpy.Describe(CLS).extent
pad = 0.04 * max(ex.width, ex.height)
# the main frame is wider than the data, so push ALL the slack east: the fire
# area hugs the west side and the top-right corner is free for the panel
_h = ex.height + 2 * pad
_w = _h * ((MAIN[2] - MAIN[0]) / (MAIN[3] - MAIN[1]))
_x0 = ex.XMin - pad
EXT = arcpy.Extent(_x0, ex.YMin - pad, _x0 + _w, ex.YMax + pad,
                   spatial_reference=arcpy.SpatialReference(2193))
EXT_TIGHT = arcpy.Extent(ex.XMin - pad, ex.YMin - pad, ex.XMax + pad, ex.YMax + pad,
                         spatial_reference=arcpy.SpatialReference(2193))


def txt(lo, x, y, s, size, name, bold=False):
    e = p.createTextElement(lo, arcpy.Point(x, y), "POINT", s, size, FONT,
                            "Bold" if bold else "Regular", None, name)
    e.setAnchor("TOP_LEFT_CORNER")
    e.elementPositionX = x
    e.elementPositionY = y
    return e


# ---- locator: local vector only, so no basemap credit block in the inset ---
for m in p.listMaps("Map_Locator_Clean"):
    p.deleteItem(m)
LOC = p.createMap("Map_Locator_Clean", "Map")
LOC.spatialReference = arcpy.SpatialReference(2193)
for l in list(LOC.listLayers()):
    if getattr(l, "isBasemapLayer", False):
        LOC.removeLayer(l)
_c = LOC.addDataFromPath(CANT)
_c.name = "Canterbury region"
_s = _c.symbology
_s.renderer.symbol.color = {'RGB': [236, 236, 233, 100]}
_s.renderer.symbol.outlineColor = {'RGB': [130, 130, 130, 100]}
_s.renderer.symbol.outlineWidth = 0.7
_c.symbology = _s
_f = LOC.addDataFromPath(PERIM)
_f.name = "Fire area"
_s = _f.symbology
_s.renderer.symbol.color = {'RGB': [200, 30, 30, 100]}
_s.renderer.symbol.outlineColor = {'RGB': [200, 30, 30, 100]}
_s.renderer.symbol.outlineWidth = 3.0
_f.symbology = _s
strip_attribution(LOC)
_ce = arcpy.Describe(CANT).extent
CANT_EXT = arcpy.Extent(_ce.XMin, _ce.YMin, _ce.XMax, _ce.YMax,
                        spatial_reference=arcpy.SpatialReference(2193))

# ---- confidence map, floated into the main map on the V3 layouts -----------
for m in p.listMaps("Map_Confidence_Inset"):
    p.deleteItem(m)
mc = p.createMap("Map_Confidence_Inset", "Map")
mc.spatialReference = arcpy.SpatialReference(2193)
for l in list(mc.listLayers()):
    if getattr(l, "isBasemapLayer", False):
        mc.removeLayer(l)
cl = mc.addDataFromPath(CONF)
cl.name = "Confidence"
_s = cl.symbology
if _s.colorizer.type != 'RasterStretchColorizer':
    _s.updateColorizer('RasterStretchColorizer')
_r = p.listColorRamps('Yellow-Orange-Brown (Continuous)') or p.listColorRamps('*Gray*')
if _r:
    _s.colorizer.colorRamp = _r[0]
cl.symbology = _s
pc = mc.addDataFromPath(PERIM)
pc.name = "2017 fire perimeter"
hollow(pc, 1.0)
strip_attribution(mc)

# ---- shared source block ---------------------------------------------------
CRED_COMMON = [
    "Data: Landsat 8 OLI Collection 2 Level-2 (USGS); LINZ 2015-16 aerial photography; LCDB;",
    "Hansen Global Forest Change v1.11 (2023). Basemap: Eagle Technology, LINZ, StatsNZ, NIWA.",
]
CRED_CRS = "Projection: NZGD2000 / New Zealand Transverse Mercator 2000 (EPSG:2193)."
CRED_SIG = "Y. Zhou, ERST619, 26 September 2026."

CRED_MAP1 = CRED_COMMON + [
    "Method: random forest, January spectra + spring 2016 composite;",
    "spatial cross-validation OA 64%, independent test 59%.",
    CRED_CRS,
    "Holes inside the perimeter are the two official unburnt islands (excluded).",
    "Bare rock is not masked; it is absorbed into the four fuel classes.",
    CRED_SIG,
]
CRED_MAP2 = CRED_COMMON + [
    "Method: dNBR from pre-/post-fire Landsat 8 NBR, offset-corrected against an",
    "unburned control ring; severity classed on the corrected dNBR.",
    CRED_CRS,
    CRED_SIG,
]

CONF_NOTE = ("Panel at top right of the map: per-pixel classification confidence "
             "(random forest max class probability); pale = least certain.")
NO_LOC_NOTE = ("Locator inset omitted to keep the main map as large as possible; "
               "the fire area is in the Port Hills, Christchurch, Canterbury.")
MAP2_NOTE = ("Locator inset is shown on Map 1 only and is not repeated here. "
             "Cells with no severity value were cloud- or shadow-masked.")


def build(lname, title, m, cls, per, credits, want_locator,
          float_map=None, extra_notes=()):
    for lo in p.listLayouts(lname):
        p.deleteItem(lo)
    lo = p.copyItem(p.listLayouts("Layout1")[0], lname) or p.listLayouts(lname)[0]
    for e in lo.listElements("TEXT_ELEMENT"):
        lo.deleteElement(e)
    for e in lo.listElements("GRAPHIC_ELEMENT"):
        if e.name in ("PanelLeft", "PanelBottom"):
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

    if float_map is not None:
        ff = lo.createMapFrame(poly(*FLOAT_INSET), float_map, "Float_" + lname)
        ff.camera.setExtent(EXT_TIGHT)

    if want_locator:
        lf = lo.createMapFrame(poly(*R_INSET), LOC, "Locator_" + lname)
        lf.camera.setExtent(CANT_EXT)
        narrow_y, legend_y = R_NARROW_Y, R_LEGEND_Y
    else:
        narrow_y, legend_y = N_NARROW_Y, N_LEGEND_Y

    na = lo.listElements("MAPSURROUND_ELEMENT", "North Arrow")[0]
    na.setAnchor("TOP_LEFT_CORNER")
    na.elementWidth = NARROW_H
    na.elementHeight = NARROW_H
    na.elementPositionX = RIGHT_X
    na.elementPositionY = narrow_y

    lg = lo.listElements("LEGEND_ELEMENT")[0]
    lg.syncNewLayer = False
    lg.syncLayerOrder = False
    for it in list(lg.items):
        lg.removeItem(it)
    lg.addItem(cls)
    lg.addItem(per)
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
    lg.elementPositionX = RIGHT_X
    lg.elementPositionY = legend_y
    lg.elementWidth = RIGHT_X2 - RIGHT_X

    sb = lo.listElements("MAPSURROUND_ELEMENT", "Scale Bar")[0]
    sd = sb.getDefinition('V3')
    sd.fittingStrategy = 'AdjustFrame'
    sd.division = 1.0
    sd.divisions = 2
    sd.subdivisions = 2
    sd.labelFrequency = 'Divisions'
    restyle(sd.labelSymbol, SZ_LEGLABEL)
    restyle(sd.unitLabelSymbol, SZ_LEGLABEL)
    sb.setDefinition(sd)
    sb.setAnchor("BOTTOM_LEFT_CORNER")
    sb.elementPositionX = RIGHT_X
    sb.elementPositionY = R_SCALE_Y

    txt(lo, MARGIN, CRED_Y, "\n".join(list(credits) + list(extra_notes)),
        SZ_CRED, "Credits")

    lo.exportToPNG(os.path.join(OUT, lname + ".png"), resolution=150)
    lo.exportToPDF(os.path.join(OUT, lname + ".pdf"), resolution=300)
    print("  ok", lname)


TITLE1 = "Pre-fire fuel classes, Port Hills, 2017"
TITLE2 = "Burn severity and unburnt refugia, Port Hills, 2017"

# name, palette, hillshade, transparency, locator, floating panel, extra notes
SPECS_MAP1 = [
    ("V3_Confidence",           PAL_CSV, False,  0, True,  mc,   (CONF_NOTE,)),
    ("V3_Confidence_NoLocator", PAL_CSV, False,  0, False, mc,   (CONF_NOTE, NO_LOC_NOTE)),
    ("V1_Report",               PAL_CSV, False,  0, True,  None, ()),
    ("V2_CVDsafe",              PAL_CVD, False,  0, True,  None, ()),
    ("V4_Terrain",              PAL_CSV, True,  30, True,  None, ()),
]

for name, pal, hs, tr, loc, floatmap, notes in SPECS_MAP1:
    m, cls, per = build_map("Map_" + name, CLS, pal, "FuelClass", FUEL_ORDER,
                            "Fuel class", hs, tr)
    build(name, TITLE1, m, cls, per, CRED_MAP1, loc, floatmap, notes)

# Map 2 -- no locator (Helen: inset on the first map only), same N arrow,
# same scale bar, same AOI extent as Map 1
m2, cls2, per2 = build_map("Map_Map2_Refugia", SEV, PAL_SEV, "ClassName",
                           SEV_ORDER, "Burn severity")
build("Map2_Refugia", TITLE2, m2, cls2, per2, CRED_MAP2,
      want_locator=False, extra_notes=(MAP2_NOTE,))

p.save()
print("saved")
print()
print("Captions for the report (below the figure; bold the 'Figure X' part):")
print("  Figure 5.8. Pre-fire fuel classes within the 2017 Port Hills fire "
      "perimeter, classified by random forest from January Landsat 8 spectra "
      "and a spring 2016 composite, with 2016 clear-fell blocks masked.")
print("  Figure 7.2. Burn severity of the 2017 Port Hills fire, classed from "
      "offset-corrected dNBR, with unburnt cells inside the perimeter shown as "
      "refugia.")
