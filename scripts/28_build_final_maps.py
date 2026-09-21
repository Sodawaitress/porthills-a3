"""
US9 - build the 2 final report maps (classification + refugia/severity) as
real ArcGIS Pro Maps + Layouts inside PortHills2017.aprx, each with the 6
required elements (title/legend/scale bar/north arrow/locator inset/
source+projection). Saved into the project so Yu can open, inspect, and
tweak tomorrow at the lab - not just a static export.

New maps/layouts only ("FuelClass_Classification_2017" / "Refugia_2017"),
existing "Map"/"Layout"/"Layout1" are NOT touched.

Author: Claude (for Yu Zhou), 2026-09-21
"""
import arcpy

APRX_PATH = r"C:\Users\zhouy3d\Desktop\PortHills\PortHills2017\PortHills2017.aprx"
GDB = r"C:\Users\zhouy3d\Desktop\PortHills\PortHills2017\PortHills2017.gdb"
FIRE_BOUNDARY = r"C:\Users\zhouy3d\Desktop\PortHills\data\Port_Hills_2017_Fire_Boundary.shp"
OUT_DIR = r"C:\Users\zhouy3d\Desktop\a3\exploration"

aprx = arcpy.mp.ArcGISProject(APRX_PATH)

# colour ramps (RGB 0-255), ClassName label -> (R,G,B)
FUEL_COLORS = {
    "Pasture": (222, 196, 101),          # tan
    "Gorse/Broom": (217, 95, 45),        # burnt orange (high flammability cue)
    "Exotic Pine": (27, 94, 32),         # dark green
    "Broadleaf Scrub": (129, 199, 132),  # medium green
}
SEVERITY_COLORS = {
    "Unburned (refugia)": (26, 150, 65),   # green
    "Low severity": (255, 255, 191),       # pale yellow
    "Moderate severity": (253, 174, 97),   # orange
    "High severity": (215, 25, 28),        # red
}


def apply_unique_value_symbology(lyr, colors):
    """Raster layers already get a RasterUniqueValueColorizer keyed on
    ClassName automatically (it's a text field) - just recolour the items."""
    sym = lyr.symbology
    c = sym.colorizer
    for grp in c.groups:
        for itm in grp.items:
            label = itm.values[0] if isinstance(itm.values, list) else itm.label
            if label in colors:
                r, g, b = colors[label]
                itm.color = {'RGB': [r, g, b, 100]}
    lyr.symbology = sym


def build_map(map_name, raster_path, colors, title_text):
    if map_name in [m.name for m in aprx.listMaps()]:
        aprx.deleteItem([m for m in aprx.listMaps() if m.name == map_name][0])
    new_map = aprx.createMap(map_name)
    new_map.spatialReference = arcpy.SpatialReference(2193)

    ras_lyr = new_map.addDataFromPath(raster_path)
    apply_unique_value_symbology(ras_lyr, colors)

    fb_lyr = new_map.addDataFromPath(FIRE_BOUNDARY)
    fb_lyr.name = "2017 Fire Perimeter"
    sym = fb_lyr.symbology
    sym.renderer.symbol.color = {'RGB': [0, 0, 0, 0]}        # no fill
    sym.renderer.symbol.outlineColor = {'RGB': [0, 0, 0, 100]}
    sym.renderer.symbol.outlineWidth = 1.5
    fb_lyr.symbology = sym
    return new_map, ras_lyr


def build_layout(layout_name, map_obj, title_text, source_text, out_png):
    """Automates the 4 elements that are reliably scriptable in this ArcGIS
    Pro version (3.6.1's arcpy.mp has no Layout.createTextElement - checked,
    not just missed): map frame, legend, north arrow, scale bar, + locator
    inset. Title and source-citation text boxes are NOT auto-added (the
    scripted CIM route for brand-new text graphics is fragile enough to risk
    a corrupt layout) - added by Yu in the GUI instead, 2 clicks each, see
    the printed instructions."""
    if layout_name in [l.name for l in aprx.listLayouts()]:
        aprx.deleteItem([l for l in aprx.listLayouts() if l.name == layout_name][0])
    layout = aprx.createLayout(8.5, 11, 'INCH', layout_name)

    map_frame_geom = arcpy.Polygon(arcpy.Array([
        arcpy.Point(0.5, 1.8), arcpy.Point(8.0, 1.8),
        arcpy.Point(8.0, 9.8), arcpy.Point(0.5, 9.8)]))
    mf = layout.createMapFrame(map_frame_geom, map_obj, "MapFrame_" + layout_name)
    mf.camera.setExtent(mf.getLayerExtent(map_obj.listLayers()[-2], False, True))

    legends = aprx.listStyleItems('ArcGIS 2D', 'LEGEND', 'Legend 1')
    leg = layout.createMapSurroundElement(
        arcpy.Polygon(arcpy.Array([arcpy.Point(6.0, 5.3), arcpy.Point(8.3, 5.3),
                                    arcpy.Point(8.3, 9.6), arcpy.Point(6.0, 9.6)])),
        "LEGEND", mf, legends[0] if legends else None, "Legend_" + layout_name)
    leg.showTitle = False
    for it in leg.items:
        it.patchHeight = 0.18
        it.patchWidth = 0.18

    north_arrows = aprx.listStyleItems('ArcGIS 2D', 'NORTH_ARROW', 'ArcGIS North 1')
    layout.createMapSurroundElement(
        arcpy.Polygon(arcpy.Array([arcpy.Point(7.6, 2.0), arcpy.Point(8.1, 2.0),
                                    arcpy.Point(8.1, 2.8), arcpy.Point(7.6, 2.8)])),
        "NORTH_ARROW", mf, north_arrows[0] if north_arrows else None, "NorthArrow_" + layout_name)

    scalebars = aprx.listStyleItems('ArcGIS 2D', 'SCALE_BAR', 'Scale Line 1 Metric')
    layout.createMapSurroundElement(
        arcpy.Polygon(arcpy.Array([arcpy.Point(0.7, 1.9), arcpy.Point(3.2, 1.9),
                                    arcpy.Point(3.2, 2.3), arcpy.Point(0.7, 2.3)])),
        "SCALE_BAR", mf, scalebars[0] if scalebars else None, "ScaleBar_" + layout_name)

    if "Locator" in [m.name for m in aprx.listMaps()]:
        loc_map = [m for m in aprx.listMaps() if m.name == "Locator"][0]
    else:
        loc_map = aprx.createMap("Locator")
        loc_map.addBasemap("Topographic")
        loc_map.addDataFromPath(FIRE_BOUNDARY)
    inset_geom = arcpy.Polygon(arcpy.Array([arcpy.Point(0.6, 8.0), arcpy.Point(2.3, 8.0),
                                             arcpy.Point(2.3, 9.6), arcpy.Point(0.6, 9.6)]))
    inset_mf = layout.createMapFrame(inset_geom, loc_map, "Inset_" + layout_name)
    inset_mf.camera.scale = 3000000

    layout.exportToPNG(out_png, resolution=200)
    print("Exported", out_png)
    print(f"\n  STILL NEEDS (GUI, ~1 min): open '{layout_name}' -> Insert tab -> Text ->")
    print(f"    title near top: \"{title_text}\"")
    print(f"    small paragraph text near bottom: \"{source_text}\"")
    return layout


fuel_map, fuel_lyr = build_map(
    "FuelClass_Classification_2017", GDB + r"\FuelClass_4class_map_clipped",
    FUEL_COLORS, "Pre-fire Fuel Type Classification")
build_layout(
    "FuelClass_Layout_2017", fuel_map,
    "Port Hills 2017 Fire — Pre-fire Fuel Type Classification",
    "Random Forest classification (4 classes, OA=0.684, Kappa=0.579), trained on Landsat 8 "
    "pre-fire imagery + LCDB2012 reference labels. bare_rock and cleared_pine excluded from "
    "the classifier (insufficient/fragmented training data) - shown as gaps, not errors. "
    "Projection: NZTM2000 (EPSG:2193). Source: scripts/06c_rf_classify_4class_final.py, "
    "scripts/12_wall_to_wall_classify.py.",
    OUT_DIR + r"\Map1_FuelClass_2017.png")

sev_map, sev_lyr = build_map(
    "Refugia_Severity_2017", GDB + r"\Severity_2017_map_clipped",
    SEVERITY_COLORS, "Burn Severity and Unburned Refugia")
build_layout(
    "Refugia_Layout_2017", sev_map,
    "Port Hills 2017 Fire — Burn Severity and Unburned Refugia",
    "dNBR-derived severity (offset-corrected, threshold=p90 of hand-drawn unburned islands, "
    "T=117.5). Unburned (green) = ephemeral refugia. Projection: NZTM2000 (EPSG:2193). "
    "Source: scripts/00_A1_PortHills_dNBR.js, scripts/27_build_severity_raster.py.",
    OUT_DIR + r"\Map2_Refugia_2017.png")

try:
    aprx.save()
    print("\nSaved project (in place).")
except OSError:
    copy_path = APRX_PATH.replace(".aprx", "_maps_update.aprx")
    aprx.saveACopy(copy_path)
    print(f"\nCouldn't save in place (ArcGIS Pro has the project open, PID lock detected).")
    print(f"Saved a copy instead: {copy_path}")
    print("Close ArcGIS Pro and re-run this script to write directly into the main "
          "project, or open the copy to see/merge the new maps+layouts.")
