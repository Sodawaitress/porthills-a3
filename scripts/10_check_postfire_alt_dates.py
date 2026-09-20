"""
US4/US6 补充 - cleared_pine 新采的19个点里,16个在post_B4(火后波段)是空值,
因为这片小区域在原来那版火后合成影像里被云/阴影盖住了。查一下火后这段时间
有没有别的干净过境日期能把这16个点的值补回来,不是重新造数据,是找一张
更干净的火后影像重新采样。

跑法：在已装好+认证过 earthengine-api 的机器上跑。
输出：打印每个候选日期在这19个点上的云污染情况,人工挑一个最干净的。
"""
import ee

ee.Initialize(project='genuine-hold-427410-f0')

AOI = ee.Geometry.Rectangle([172.55, -43.65, 172.67, -43.56])

# 19个 cleared_pine 点 (OID, lon, lat) -- 跟 TrainingPoints_raw 一致
CP_POINTS = [
    (337, 172.632306, -43.599119), (338, 172.630504, -43.598650),
    (339, 172.631001, -43.598564), (340, 172.631509, -43.598260),
    (341, 172.630621, -43.598249), (342, 172.627061, -43.601907),
    (343, 172.632479, -43.600771), (344, 172.629901, -43.601387),
    (345, 172.630651, -43.599171), (346, 172.627142, -43.602177),
    (347, 172.632306, -43.600531), (348, 172.627499, -43.601776),
    (349, 172.629889, -43.598052), (350, 172.627617, -43.601512),
    (351, 172.632022, -43.598024), (352, 172.632337, -43.598794),
    (353, 172.629945, -43.601076), (354, 172.632775, -43.602354),
    (355, 172.632400, -43.600186),
]

fc = ee.FeatureCollection([ee.Feature(ee.Geometry.Point([lon, lat]), {'OID': oid})
                            for oid, lon, lat in CP_POINTS])

# 火后窗口：起火2017-02-13，往后拉宽到5月，看有没有更干净的过境
POST_START = '2017-02-13'
POST_END = '2017-06-01'

l8 = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
        .filterBounds(AOI)
        .filterDate(POST_START, POST_END)
        .sort('CLOUD_COVER'))

n_images = l8.size().getInfo()
print('火后候选影像数(2017-02-13 ~ 2017-06-01):', n_images)

imgs = l8.toList(n_images)
for i in range(n_images):
    img = ee.Image(imgs.get(i))
    date = ee.Date(img.get('system:time_start')).format('YYYY-MM-dd').getInfo()
    cloud_cover_scene = img.get('CLOUD_COVER').getInfo()

    qa = img.select('QA_PIXEL')
    cloud_mask = (qa.bitwiseAnd(1 << 1).Or(qa.bitwiseAnd(1 << 2))
                    .Or(qa.bitwiseAnd(1 << 3)).Or(qa.bitwiseAnd(1 << 4)))
    clear = cloud_mask.Not().rename('clear')

    sampled = clear.sampleRegions(collection=fc, scale=30, geometries=False).getInfo()
    n_clear = sum(1 for f in sampled['features'] if f['properties'].get('clear') == 1)

    print(f'{date}  scene_cloud={cloud_cover_scene:.1f}%  '
          f'19点里干净的={n_clear}/19')

print('\n找 n_clear 最大(最好=19)的那一天,把它的 SR_B2-B7 加权进post-fire合成,'
      '重新给这19个点(尤其之前valid_data=0的16个)采样一次。')
