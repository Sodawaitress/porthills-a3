// ============================================================
// ERST619 Fire Assessment - 2024 Port Hills fire dNBR (online GEE, JavaScript)
// Usage: open code.earthengine.google.com -> paste -> click Run
// Fire: 2024-02-14 (Worsleys Rd); operations completed 2024-03-13
// ============================================================

// 1. Study area AOI - covers the actual 2024 + 2017 fire footprints (ECan official extents)
var aoi = ee.Geometry.Rectangle([172.55, -43.65, 172.67, -43.56]);
Map.centerObject(aoi, 12);

// 2. Pre-fire / post-fire date windows (tight, bracketing the fire to cut seasonal drift)
var preStart  = '2024-01-10', preEnd  = '2024-02-13';   // ~1 month before, still summer
var postStart = '2024-02-20', postEnd = '2024-03-31';   // just after containment, still summer

// 3. Cloud filter: use SCL band to drop cloud shadow(3)/med cloud(8)/high cloud(9)/cirrus(10)/snow(11)
function maskS2(img) {
  var scl = img.select('SCL');
  var mask = scl.neq(3).and(scl.neq(8)).and(scl.neq(9))
                .and(scl.neq(10)).and(scl.neq(11));
  return img.updateMask(mask).divide(10000);   // reflectance 0-10000 -> 0-1
}

// 4. Cloud-free median composite for a date window (extra filter: scene cloudiness < 40%)
function getS2(start, end) {
  return ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(aoi)
    .filterDate(start, end)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 40))
    .map(maskS2)
    .median()
    .clip(aoi);
}
var preImg  = getS2(preStart,  preEnd);
var postImg = getS2(postStart, postEnd);

// Count how many usable scenes are in each window (check the Console)
print('Pre-fire scene count', ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(aoi).filterDate(preStart, preEnd)
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 40)).size());
print('Post-fire scene count', ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
  .filterBounds(aoi).filterDate(postStart, postEnd)
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 40)).size());

// 5. NBR = (NIR-SWIR2)/(NIR+SWIR2);  S2: NIR=B8, SWIR2=B12
function nbr(img) { return img.normalizedDifference(['B8', 'B12']).rename('NBR'); }
var preNBR  = nbr(preImg);
var postNBR = nbr(postImg);

// dNBR = pre - post (burned areas lose NBR -> positive dNBR), x1000 (USGS convention)
var dnbr = preNBR.subtract(postNBR).multiply(1000).rename('dNBR');

// 6. Burn severity classes (USGS thresholds)
var severity = dnbr
  .where(dnbr.lt(100), 1)                              // unburned / unburned patch (refugia)
  .where(dnbr.gte(100).and(dnbr.lt(270)), 2)          // low
  .where(dnbr.gte(270).and(dnbr.lt(660)), 3)          // moderate
  .where(dnbr.gte(660), 4);                            // high

// 7. Display
var rgbVis = {bands: ['B4', 'B3', 'B2'], min: 0, max: 0.3};
Map.addLayer(preImg,  rgbVis, 'Pre-fire true colour');
Map.addLayer(postImg, rgbVis, 'Post-fire true colour');
Map.addLayer(dnbr, {min: -500, max: 1000,
  palette: ['0000ff', 'ffffff', 'ffff00', 'ff8000', 'ff0000']}, 'dNBR');
Map.addLayer(severity, {min: 1, max: 4,
  palette: ['1a9850', 'ffffbf', 'fdae61', 'd73027']}, 'Burn severity');
Map.addLayer(aoi, {color: 'black'}, 'AOI', false);

// 8. (Optional) Export dNBR to Google Drive - run from the Tasks tab
Export.image.toDrive({
  image: dnbr,
  description: 'PortHills_2024_dNBR',
  folder: 'ERST619_Fire',
  region: aoi,
  scale: 10,
  crs: 'EPSG:2193',      // NZTM2000, official NZ projection
  maxPixels: 1e9
});
