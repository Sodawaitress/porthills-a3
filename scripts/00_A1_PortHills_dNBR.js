// A1 原始脚本 PortHills_dNBR — 从 A1 报告 docx 完整提取(👤Yu 自己的 GEE JS，原样保存非重写)
// 用途：A3 完善 2017 直接复用/参考——智能掩膜(烧痕≠shadow)、offset 校正、岛屿 p90 阈值、岛屿验证。
// 原始上下文 = Kaupapa Tuhika 1 Data Exploration。配套真数字见 plan_2017_improvements.md。

//==========================
//ERST619 Kaupapa Tuhika 1 | Data Exploration and Visualisation
//==========================
//Purpose: Map burned area and unburned refugia, Port Hills fire 2017
//Dataset: Landsat 8 Collection 2 Level 2 surface reflectance
//script name PortHills_dNBR
//==========================

//==========================
// 1. STUDY AREA (AOI)
//==========================
var ASSET_ID = 'projects/genuine-hold-427410-f0/assets/Port_Hills_2017_Fire_Boundary';
var raw = ee.FeatureCollection(ASSET_ID);

var fireWithHoles = raw.filter(ee.Filter.eq('Type','Fire Boundary')).first().geometry();
var unburntFC     = raw.filter(ee.Filter.eq('Type','Unburnt'));
var aoi           = fireWithHoles.union(unburntFC.geometry(), 1);  //fill the two holes
var wideFrame     = aoi.buffer(4000);   //wide enough for the control ring
var mapFrame      = aoi.buffer(500);    //display extent only

var ha        = 10000;
var pixelArea = ee.Image.pixelArea();

function haIn(mask, geom){
  return pixelArea.updateMask(mask).reduceRegion({
    reducer: ee.Reducer.sum(), geometry: geom || aoi,
    scale: 30, maxPixels: 1e9}).getNumber('area').divide(ha);
}

Map.centerObject(aoi, 13);
Map.setOptions('SATELLITE');

//source file is Web Mercator; .area() is geodesic so it is correct
print('===== OFFICIAL MAP (ha) =====');
print('perimeter:',        aoi.area(1).divide(ha));
print('official unburnt:', unburntFC.geometry().area(1).divide(ha));
print('official burned:',  fireWithHoles.area(1).divide(ha));

//==========================
// 2. STUDY PERIOD AND OUTPUT SETTINGS
//==========================
var preStart  = '2016-12-01';   //widened back for cloud-free coverage
var preEnd    = '2017-02-11';   //fire ignited 13 Feb
var postStart = '2017-02-24';   //hotspots ran to about 25 Feb
var postEnd   = '2017-03-30';   //kept short; regrowth lifts NBR

var outputBands = ['SR_B2','SR_B3','SR_B4','SR_B5','SR_B6','SR_B7'];
//                  blue    green   red     NIR     SWIR1   SWIR2
var outputScale = 30;
var outputCRS   = 'EPSG:2193';  //NZ Transverse Mercator, for correct areas

//==========================
// 3. TERRAIN
//==========================
var dem       = ee.Image('USGS/SRTMGL1_003').rename('elev');
var slope     = ee.Terrain.slope(dem).rename('slope');
//northness, not aspect: 359 and 1 degrees are 358 apart as numbers
var northness = ee.Terrain.aspect(dem).multiply(Math.PI/180).cos().rename('northness');
var terrain   = dem.addBands(slope).addBands(northness);

var firePct = terrain.select(['elev','slope']).reduceRegion({
  reducer: ee.Reducer.percentile([2,98]),
  geometry: aoi, scale: outputScale, maxPixels: 1e9});

//==========================
// 4. LOAD LANDSAT AND MASK CLOUD
//==========================
//Collection 2 needs an offset as well as a scale factor
function scaleSR(image){
  return ee.Image(image.select('SR_B.').multiply(0.0000275).add(-0.2)
    .copyProperties(image, ['system:time_start']));  //ee.Image() wrapper is required
}

//QA_PIXEL bits: 3 = cloud, 4 = cloud shadow
//shadow flag removed 242 ha of high-dNBR ground inside the fire,
//flagged in all five scenes, so it was reading char not shadow
function maskL8clouds_QA(image){
  var qa = image.select('QA_PIXEL');
  var inFire = ee.Image.constant(1).clip(aoi).mask();
  var bad = qa.bitwiseAnd(1 << 3).neq(0)                    //cloud, everywhere
    .or(qa.bitwiseAnd(1 << 4).neq(0).and(inFire.not()));    //shadow, outside only
  return scaleSR(image).updateMask(bad.not());
}

var l8      = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2').filterBounds(wideFrame);
var preCol  = l8.filterDate(preStart,  preEnd ).map(maskL8clouds_QA);
var postCol = l8.filterDate(postStart, postEnd).map(maskL8clouds_QA);

var pre  = preCol.select(outputBands).median().clip(wideFrame);
var post = postCol.select(outputBands).median().clip(wideFrame);

var both = pre.select('SR_B5').mask().and(post.select('SR_B5').mask());
//dNBR needs valid pixels on both dates, so coverage is the overlap

print('===== COVERAGE =====');
print('pre-fire scenes:',  preCol.size());
print('post-fire scenes:', postCol.size());
print('dNBR computable (ha):', haIn(both));
print('coverage %:', haIn(both).divide(1758.88).multiply(100));
print('cloud gap (ha):', ee.Number(1758.88).subtract(haIn(both)));

//==========================
// 5. SPECTRAL INDICES
//==========================
//--------------------------
// NBR, Key & Benson (2006)
// Formula: (NIR - SWIR2) / (NIR + SWIR2)
// Fire drops NIR and raises SWIR2, so the difference is amplified
//--------------------------
var nbrPre  = pre.normalizedDifference(['SR_B5','SR_B7']).rename('NBR_pre');
var nbrPost = post.normalizedDifference(['SR_B5','SR_B7']).rename('NBR_post');
var dnbrRaw = nbrPre.subtract(nbrPost).multiply(1000).rename('dNBR');  //x1000, USGS convention

//--------------------------
// NDVI, pre-fire only, for the vegetation mask
// Formula: (NIR - Red) / (NIR + Red)
// Rock and roads are stable in both scenes and would read as unburned
//--------------------------
var ndviPre = pre.normalizedDifference(['SR_B5','SR_B4']).rename('NDVI');
var vegMask = ndviPre.gt(0.25);
var valid   = both.and(vegMask);

//--------------------------
// BSI, an independent check on where bare ground is
// Formula: ((Red+SWIR)-(NIR+Blue)) / ((Red+SWIR)+(NIR+Blue))
//--------------------------
var bsi = pre.expression(
  '((RED + SWIR) - (NIR + BLUE)) / ((RED + SWIR) + (NIR + BLUE))', {
    RED:  pre.select('SR_B4'), SWIR: pre.select('SR_B6'),
    NIR:  pre.select('SR_B5'), BLUE: pre.select('SR_B2')
  }).rename('BSI');

//==========================
// 6. OFFSET CORRECTION
//==========================
//unburned vegetation should read zero; whatever it reads is seasonal drift
//control ring matched to the fire on elevation, slope and cover type
//crops excluded: a paddock cut between the dates looks like a burn

var dw = ee.ImageCollection('GOOGLE/DYNAMICWORLD/V1')
  .filterDate('2016-12-01','2017-02-12').filterBounds(wideFrame)
  .select('label').mode();
var water = ee.Image('JRC/GSW1_4/GlobalSurfaceWater').select('max_extent').unmask(0);

var ring = aoi.buffer(2000).difference(aoi.buffer(500), 1);
//500 m inner setback avoids scorch beyond the containment line

var controlMask = ee.Image.constant(1).clip(ring).mask()
  .and(dem.gte(ee.Number(firePct.get('elev_p2'))))
  .and(dem.lte(ee.Number(firePct.get('elev_p98'))))
  .and(slope.gte(ee.Number(firePct.get('slope_p2'))))
  .and(dw.eq(1).or(dw.eq(2)).or(dw.eq(5)))   //trees, grass, shrub only
  .and(dw.neq(4))                             //no crops
  .and(water.eq(0)).and(vegMask).selfMask();

var ctrl = dnbrRaw.updateMask(controlMask).reduceRegion({
  reducer: ee.Reducer.mean().combine(ee.Reducer.stdDev(), null, true),
  geometry: ring, scale: outputScale, maxPixels: 1e9});

var offset = ee.Number(ctrl.get('dNBR_mean'));
var ctrlSD = ee.Number(ctrl.get('dNBR_stdDev'));
var dnbr   = dnbrRaw.subtract(offset).rename('dNBR');

print('===== OFFSET =====');
print('mean dNBR on unburned control:', offset);
print('standard deviation:', ctrlSD);
print('control area (ha):', haIn(controlMask, ring));

//==========================
// 7. THRESHOLD
//==========================
//refugia sit in gullies and shaded slopes, so they cure less than the control
//the two mapped islands are unburned ground INSIDE the fire, a better null
//90th percentile keeps 90% of known refugia unburned by construction
//a percentile, not mean+2sd, because the tail inflates the sd
//Otsu was tested and rejected: it cut inside the burned group

var islCore = unburntFC.geometry();

var islPct = dnbr.updateMask(valid).reduceRegion({
  reducer: ee.Reducer.percentile([50,90,95]),
  geometry: islCore, scale: outputScale, maxPixels: 1e9});

var T = ee.Number(islPct.get('dNBR_p90'));

function falsePositiveRate(t){
  return dnbr.gt(t).updateMask(controlMask).reduceRegion({
    reducer: ee.Reducer.mean(), geometry: ring,
    scale: outputScale, maxPixels: 1e9}).getNumber('dNBR');
}

print('===== THRESHOLD =====');
print('island dNBR p50 / p90 / p95:',
      islPct.values(['dNBR_p50','dNBR_p90','dNBR_p95']));
print('T:', T);
print('2 x control sd would give:', ctrlSD.multiply(2));
print('commission error at T:', falsePositiveRate(T));

print(ui.Chart.image.histogram({
  image: dnbr.updateMask(vegMask), region: aoi, scale: outputScale, maxBuckets: 120
}).setOptions({title:'dNBR, offset corrected, vegetated ground',
               hAxis:{title:'dNBR x1000'}, vAxis:{title:'pixels'}}));

//==========================
// 8. CLASSIFY AND MEASURE
//==========================
//burned break from my own data; 270 and 660 kept from USGS for comparability
var severity = ee.Image(0)
  .where(dnbr.gt(T),   1)
  .where(dnbr.gt(270), 2)
  .where(dnbr.gt(660), 3)
  .updateMask(valid).rename('severity');

function burnedHa(t){ return haIn(valid.and(dnbr.gt(t))); }

var covered  = haIn(valid);
var burned   = burnedHa(T);
var unburned = haIn(valid.and(dnbr.lte(T)));

print('===== AREAS (ha), covered ground only =====');
print('covered:',   covered);
print('burned:',    burned);
print('unburned:',  unburned);
print('sensitivity T-50 / T+50:', burnedHa(T.subtract(50)), burnedHa(T.add(50)));
print('burned rate %:', burned.divide(covered).multiply(100));
//assumes cloudy ground burned at the same rate as clear ground
print('scaled to the perimeter:', burned.divide(covered).multiply(1758.88));

//how much unburned ground did the hand-drawn map miss?
var inIslands = haIn(valid.and(dnbr.lte(T)), unburntFC.geometry());
print('===== UNMAPPED REFUGIA =====');
print('my unburned total:', unburned);
print('inside the two official islands:', inIslands);
print('NEW unmapped refugia (ha):', unburned.subtract(inIslands));
print('scaled to the perimeter:',
      unburned.subtract(inIslands).divide(covered.divide(1758.88)));

//==========================
// 9. VALIDATION
//==========================
//the two islands were mapped by hand, so they are independent reference data
var diag = unburntFC.map(function(f){
  var g = f.geometry();
  return f.set({
    recall: dnbr.lte(T).updateMask(valid).reduceRegion({
      reducer: ee.Reducer.mean(), geometry: g,
      scale: outputScale, maxPixels: 1e8}).get('dNBR'),
    mean_dnbr: dnbr.updateMask(valid).reduceRegion({
      reducer: ee.Reducer.mean(), geometry: g,
      scale: outputScale, maxPixels: 1e8}).get('dNBR'),
    covered_ha: haIn(valid, g)
  });
});

print('===== VALIDATION =====');
print('mapped area (ha):', unburntFC.aggregate_array('Area'));
print('covered (ha):',     diag.aggregate_array('covered_ha'));
print('mean dNBR inside:', diag.aggregate_array('mean_dnbr'));
print('recall:',           diag.aggregate_array('recall'));
print('officially burned ground also called burned:',
  dnbr.gt(T).updateMask(valid).reduceRegion({
    reducer: ee.Reducer.mean(), geometry: fireWithHoles,
    scale: outputScale, maxPixels: 1e9}).get('dNBR'));

//==========================
// 10. VISUALISATION
//==========================
//reflectance is 0-1 after scaling, so max is 0.3-0.4, not 3000
//set stretches separately for pre and post; the post surface is darker
Map.addLayer(pre.clip(mapFrame),  {bands:['SR_B4','SR_B3','SR_B2'], min:0, max:0.3},
             '1a Natural colour PRE', false);
Map.addLayer(post.clip(mapFrame), {bands:['SR_B4','SR_B3','SR_B2'], min:0, max:0.3},
             '1b Natural colour POST', false);
Map.addLayer(pre.clip(mapFrame),  {bands:['SR_B5','SR_B4','SR_B3'], min:0, max:0.4},
             '2a Colour infrared PRE', false);
Map.addLayer(post.clip(mapFrame), {bands:['SR_B5','SR_B4','SR_B3'], min:0, max:0.4},
             '2b Colour infrared POST', false);

//burn composite: red = SWIR2 which rises, green = NIR which falls
Map.addLayer(pre.clip(mapFrame),  {bands:['SR_B7','SR_B5','SR_B4'], min:0, max:0.4},
             '3a Burn SWIR composite PRE', false);
Map.addLayer(post.clip(mapFrame), {bands:['SR_B7','SR_B5','SR_B4'], min:0, max:0.4},
             '3b Burn SWIR composite POST', true);

Map.addLayer(ndviPre.clip(mapFrame), {min:-0.2, max:0.8,
  palette:['blue','white','yellow','green','darkgreen']}, '4 NDVI pre-fire', false);
Map.addLayer(bsi.clip(mapFrame), {min:-0.5, max:0.5,
  palette:['darkgreen','yellow','orange','brown','white']}, '5 Bare Soil Index', false);
Map.addLayer(dnbr.updateMask(valid).clip(mapFrame), {min:-200, max:800,
  palette:['2c7bb6','ffffbf','d7191c']}, '6 dNBR corrected', false);  //diverging, centred on 0

Map.addLayer(severity.clip(mapFrame), {min:0, max:3,
  palette:['1a9641','ffffbf','fdae61','d7191c']}, '7 Severity', true);
Map.addLayer(both.not().selfMask().clip(mapFrame), {palette:'808080'},
             '8 No data (cloud)', true, 0.75);  //never white; white reads as unburned

Map.addLayer(ee.Image().paint(ee.FeatureCollection([ee.Feature(aoi)]), 0, 3),
             {palette:'ffcc00'}, '9 Fire perimeter', true);
Map.addLayer(ee.Image().paint(unburntFC, 0, 2),
             {palette:'00ffff'}, '10 Official unburnt islands', true);

//unclipped: the rectangular patches west are cut paddocks, not fire
//evidence that this index detects vegetation removal, not combustion
Map.addLayer(dnbr.gt(T).updateMask(vegMask).selfMask(), {palette:'d7191c'},
             '11 Wide view, note the paddock shapes', false);

//==========================
// 11. EXPORT TO GEOTIFF
//==========================
//band names are lost in GeoTIFF, so the order is:
//1-6 pre_B2..B7  7-12 post_B2..B7  13 NBR_pre  14 NBR_post  15 dNBR
//16 NDVI  17 BSI  18 severity  19 valid_data  20 elev  21 slope  22 northness
var stack = pre.rename(['pre_B2','pre_B3','pre_B4','pre_B5','pre_B6','pre_B7'])
  .addBands(post.rename(['post_B2','post_B3','post_B4','post_B5','post_B6','post_B7']))
  .addBands(nbrPre).addBands(nbrPost).addBands(dnbr)
  .addBands(ndviPre).addBands(bsi)
  .addBands(severity).addBands(both.rename('valid_data'))
  .addBands(terrain)
  .toFloat();

Export.image.toDrive({
  image: stack,
  description: 'PortHills2017_stack',
  folder: 'GEE_exports',
  fileNamePrefix: 'PortHills2017_stack',
  region: aoi.buffer(500),
  scale: outputScale,
  crs: outputCRS,
  maxPixels: 1e13,
  fileFormat: 'GeoTIFF'
});

Export.table.toDrive({
  collection: diag,
  description: 'PortHills2017_island_validation',
  folder: 'GEE_exports',
  fileFormat: 'CSV'
});
//==========================
