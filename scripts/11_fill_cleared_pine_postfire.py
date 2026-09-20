"""
Fill the 19 cleared_pine points' missing POST-fire columns.
(Only post-fire is missing; pre bands / indices / terrain are already valid in
the complete table. Root cause: post-fire cloud hole -> valid_data=0.)
Script 10 found 2017-04-22 is clean (19/19). Re-sample post_B2-B7 from that date,
compute NBR_post + dNBR (dNBR = existing NBR_pre - NBR_post), set valid_data=1.
Real 2017-04-22 imagery, not fabricated.

Output: scripts/cleared_pine_postfire_fill.csv  -- long column names, join into
complete table by OID (drop into the 19 cleared_pine rows).
Run: python3 11_fill_cleared_pine_postfire.py   (GEE, this machine)
"""
import ee, os, csv
ee.Initialize(project='genuine-hold-427410-f0')

HERE = os.path.dirname(os.path.abspath(__file__))
COMPLETE = os.path.join(HERE, "PortHills_PointTable_complete.csv")
OUT = os.path.join(HERE, "cleared_pine_postfire_fill.csv")
AOI = ee.Geometry.Rectangle([172.55, -43.65, 172.67, -43.56])
P = "PortHills2017_stack_"                    # complete table uses long column names

CP = [(337,172.632306,-43.599119),(338,172.630504,-43.598650),(339,172.631001,-43.598564),
      (340,172.631509,-43.598260),(341,172.630621,-43.598249),(342,172.627061,-43.601907),
      (343,172.632479,-43.600771),(344,172.629901,-43.601387),(345,172.630651,-43.599171),
      (346,172.627142,-43.602177),(347,172.632306,-43.600531),(348,172.627499,-43.601776),
      (349,172.629889,-43.598052),(350,172.627617,-43.601512),(351,172.632022,-43.598024),
      (352,172.632337,-43.598794),(353,172.629945,-43.601076),(354,172.632775,-43.602354),
      (355,172.632400,-43.600186)]

# NBR_pre per OID from complete (long name) -> for dNBR
nbr_pre = {}
for r in csv.DictReader(open(COMPLETE)):
    if r.get("FuelClass") == "cleared_pine" and str(r.get(P+"NBR_pre","")).strip():
        nbr_pre[int(r["OID"])] = float(r[P+"NBR_pre"])

def prep(img):
    qa = img.select('QA_PIXEL')
    cloud = (qa.bitwiseAnd(1<<1).Or(qa.bitwiseAnd(1<<2))
               .Or(qa.bitwiseAnd(1<<3)).Or(qa.bitwiseAnd(1<<4)))
    return img.select('SR_B.').multiply(0.0000275).add(-0.2).updateMask(cloud.Not())

post = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
        .filterBounds(AOI).filterDate('2017-04-22','2017-04-23').map(prep).median()
        .select(['SR_B2','SR_B3','SR_B4','SR_B5','SR_B6','SR_B7'],
                ['B2','B3','B4','B5','B6','B7']))

fc = ee.FeatureCollection([ee.Feature(ee.Geometry.Point([lon,lat]), {'OID':oid})
                           for oid,lon,lat in CP])
sampled = post.sampleRegions(collection=fc, scale=30, geometries=False).getInfo()

bands = ['post_B2','post_B3','post_B4','post_B5','post_B6','post_B7']
cols = ['OID'] + [P+b for b in bands] + [P+'NBR_post', P+'dNBR', P+'valid_data']
rows = []
for f in sampled['features']:
    p = f['properties']; oid = int(p['OID'])
    nbr_post = (p['B5']-p['B7'])/(p['B5']+p['B7'])
    row = {'OID': oid}
    for b, k in zip(bands, ['B2','B3','B4','B5','B6','B7']):
        row[P+b] = round(p[k], 6)
    row[P+'NBR_post'] = round(nbr_post, 6)
    row[P+'dNBR'] = round(nbr_pre[oid]-nbr_post, 6) if oid in nbr_pre else ''
    row[P+'valid_data'] = 1
    rows.append(row)

rows.sort(key=lambda r: r['OID'])
with open(OUT,'w',newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
print(f"filled {len(rows)}/19 -> {OUT}")
print("dNBR 算出来的点数:", sum(1 for r in rows if r[P+'dNBR']!=''))
print("sample:", {k:rows[0][k] for k in ['OID', P+'post_B4', P+'NBR_post', P+'dNBR', P+'valid_data']})
