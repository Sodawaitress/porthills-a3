// ============================================================
// ERST619 - 2024 Port Hills: Hansen forest-loss mask (2017-2023),
// same method as the 2017 project's cleared_pine (06_cleared_pine_from_hansen.py),
// extended to a year RANGE instead of a single year, since we're now asking
// "has this pine footprint recovered a closed canopy at any point since the
// 2017 fire, or not" rather than "did it get cut the year before the fire".
//
// Usage: open code.earthengine.google.com -> paste -> Run -> Tasks tab -> export.
// Needs to run somewhere already authenticated to Earth Engine (this machine's
// Python env isn't - see chat). Output: GeoTIFF to Drive, then bring it back
// into ArcGIS Pro locally to intersect with the Name_2012 "Exotic Forest"
// polygon (already extracted, 225.52 ha) and apply the same blocky-patch filter
// 2017 used (connectedPixelCount >= 6 px @ 30m, drops scattered noise).
// ============================================================

// 1. AOI - western Port Hills, covers both 2017 and 2024 fire footprints
var aoi = ee.Geometry.Rectangle([172.55, -43.65, 172.67, -43.56]);
Map.centerObject(aoi, 12);

// 2. Hansen Global Forest Change - lossyear band, encode: 1-23 = loss in 2001-2023
var hansen = ee.Image('UMD/hansen/global_forest_change_2023_v1_11');
var lossyear = hansen.select('lossyear').clip(aoi);
var treecover2000 = hansen.select('treecover2000').clip(aoi);

// 3. loss any time 2017-2023 (code 17-23) - i.e. "disturbed at or after the fire,
//    and Hansen has not shown it regrowing past its detection threshold since"
var lossSince2017 = lossyear.gte(17).and(lossyear.lte(23));

// 4. blocky-patch filter (same threshold as 2017: >=6 connected 30m pixels ~0.5ha)
//    drops single-pixel noise / soft cloud-edge false positives
var size = lossSince2017.selfMask().connectedPixelCount({maxSize: 128, eightConnected: true});
var blocks = lossSince2017.selfMask().updateMask(size.gte(6));

// 5. display
Map.addLayer(treecover2000, {min: 0, max: 100, palette: ['ffffff', '00ff00']}, 'Tree cover 2000', false);
Map.addLayer(lossyear, {min: 1, max: 23, palette: ['ffff00', 'ff8000', 'ff0000']}, 'Loss year (raw)', false);
Map.addLayer(blocks, {palette: ['ff00ff']}, 'Loss 2017-2023, blocky patches only');
Map.addLayer(aoi, {color: 'black'}, 'AOI', false);

// area check
var pixelHa = ee.Image.pixelArea().divide(10000);
var lossHa = pixelHa.updateMask(blocks).reduceRegion({
  reducer: ee.Reducer.sum(), geometry: aoi, scale: 30, maxPixels: 1e9});
print('Blocky forest-loss area 2017-2023 inside AOI rectangle (ha)', lossHa);

// 6. export mask (1 = loss block, else masked) - EPSG:2193 to match everything else
Export.image.toDrive({
  image: blocks.rename('loss_2017_2023'),
  description: 'PortHills_2024_hansen_loss_2017_2023',
  folder: 'ERST619_Fire',
  region: aoi,
  scale: 30,
  crs: 'EPSG:2193',
  maxPixels: 1e9
});
