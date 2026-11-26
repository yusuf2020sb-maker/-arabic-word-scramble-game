"""Builds shamkha/index.html (one self-contained file) for مرطبات الشامخة.

Edit MENU / CONTACT below, then run:  python3 shamkha/build.py
Photos come from shamkha/img/menu (taken from the restaurant's own Google Site) and are
embedded as small WebP images so the single HTML file works anywhere (WhatsApp, Files, Safari).
"""
import base64, io, json, os, urllib.parse
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img', 'menu')

CONTACT = {
    'whatsapp': '971565075660', 'whatsapp_show': '056 507 5660',
    'mobile': '971505804964', 'mobile_show': '050 580 4964',
    'landline': '97125845154', 'landline_show': '02 584 5154',
    'address': 'شارع جبل بركة، الشامخة، أبوظبي',
    'hours': '٢٤ ساعة، كل يوم',
}

# The two size ladders the restaurant publishes for its fuala dishes (AED).
LADDER_A = [['صغير', 24], ['وسط', 35], ['كبير', 55], ['٥ أشخاص', 89], ['٧ أشخاص', 132], ['١٠ أشخاص', 187], ['١٥ شخص', 320]]
LADDER_B = [['صغير', 12], ['وسط', 22], ['كبير', 42], ['٥ أشخاص', 63], ['٧ أشخاص', 94], ['١٠ أشخاص', 126], ['١٥ شخص', 262]]

# Every item on the restaurant's site. desc = a short plain description of the dish.
MENU = [
  {'id': 'fuala', 'name': 'الفوالة', 'intro': 'أطباق الضيافة الإماراتية، بالأحجام من صحن لشخص إلى قدر يكفي ١٥ شخص.', 'items': [
    {'id': 'madrooba', 'name': 'مضروبة', 'img': 'fuala-01', 'options': ['لحم', 'دجاج'], 'prices': LADDER_A,
     'desc': 'طحين وبهارات يتطبخ مع اللحم أو الدجاج حتى يصير قوامه ناعم، ويتقدم مع الليمون.'},
    {'id': 'arsiya', 'name': 'عرسية', 'img': 'fuala-02', 'options': ['لحم', 'دجاج'], 'prices': LADDER_A,
     'desc': 'رز مطبوخ مع اللحم أو الدجاج حتى يتهرس، بالسمن والبصل المحمّر، طبق الأعراس.'},
    {'id': 'marqooqa', 'name': 'مرقوقة', 'img': 'fuala-03', 'options': ['لحم', 'دجاج'], 'prices': LADDER_A,
     'desc': 'رقائق عجين تتطبخ في مرق الخضار مع اللحم أو الدجاج.'},
    {'id': 'harees', 'name': 'هريس', 'img': 'fuala-04', 'options': ['لحم', 'دجاج'], 'prices': LADDER_A,
     'desc': 'حب الهريس يتطبخ ساعات مع اللحم أو الدجاج حتى ينهرس، ويتقدم بالسمن.'},
    {'id': 'aseeda', 'name': 'عصيدة', 'img': 'fuala-05', 'prices': LADDER_A,
     'desc': 'عصيدة بالزعفران والهيل، مزينة بالفستق.'},
    {'id': 'sago', 'name': 'ساقو', 'img': 'fuala-06', 'prices': LADDER_A,
     'desc': 'ساقو بالزعفران والسكر، مزين بالفستق والكاجو.'},
    {'id': 'khabeesa', 'name': 'خبيصة', 'img': 'fuala-07', 'prices': LADDER_A,
     'desc': 'طحين محمّص بالسمن والسكر والزعفران، مزين بالفستق والكاجو.'},
    {'id': 'qurs', 'name': 'قرص', 'img': 'fuala-08', 'prices': LADDER_A,
     'desc': 'قرص بالتمر والزعفران، مزين بالمكسرات.'},
    {'id': 'khubz-laban', 'name': 'خبز ولبن', 'img': 'fuala-09', 'prices': LADDER_B,
     'desc': 'خبز رقاق مع لبن بارد.'},
    {'id': 'khanfaroosh', 'name': 'خنفروش', 'img': 'fuala-10', 'prices': LADDER_B,
     'desc': 'حلوى مقلية بالزعفران والهيل، تتقدم مع العسل.'},
    {'id': 'balaleet', 'name': 'بلاليط', 'img': 'fuala-11', 'prices': LADDER_B,
     'desc': 'شعيرية بالسكر والزعفران والهيل، ومعها بيض.'},
    {'id': 'nakhi', 'name': 'نخي', 'img': 'fuala-12', 'prices': LADDER_B,
     'desc': 'حمص مسلوق بالبهارات والليمون.'},
  ]},
  {'id': 'trays', 'name': 'الصواني', 'intro': 'كل صينية معها ١٢ حبة خبز ودلة كرك.', 'items': [
    {'id': 'riyooq', 'name': 'صواني الريوق', 'img': 'tray-01', 'prices': [['الصينية', 157]],
     'desc': 'صينية بلاستيك فيها ٥ أصناف، مع ١٢ حبة خبز ودلة كرك.'},
    {'id': 'lamma', 'name': 'صواني اللمة', 'img': 'tray-02', 'prices': [['صغير', 157], ['وسط', 210], ['كبير', 315]],
     'desc': 'صينية فيها ٥ أصناف، مع ١٢ حبة خبز ودلة كرك.'},
    {'id': 'turathiya', 'name': 'الصينية التراثية', 'img': 'home-02', 'prices': [['صغير', 260], ['وسط', 315], ['كبير', 420]],
     'desc': 'صينية تراثية فيها ٧ أصناف، مع ١٢ حبة خبز ودلة كرك.'},
    {'id': 'box', 'name': 'بوكس الريوق', 'img': 'sw-03', 'prices': [],
     'desc': 'بوكس فيه ٤ أصناف من اختياركم.'},
  ]},
  {'id': 'rice', 'name': 'العيوش', 'intro': 'اختار نوع الرز: أبيض، برياني، مجبوس، مندي، أو زربيان.', 'items': [
    {'id': 'rice-meat', 'name': 'عيش باللحم', 'img': 'rice-01', 'options': ['مندي', 'برياني', 'مشوي', 'زربيان', 'مجبوس', 'مقلوبة', 'صالونة'], 'prices': [],
     'desc': 'لحم مع الرز اللي تختاره: أبيض، برياني، مجبوس، مندي، أو زربيان.'},
    {'id': 'rice-chicken', 'name': 'عيش بالدجاج', 'img': 'rice-02', 'options': ['مندي', 'برياني', 'مشوي', 'زربيان', 'مجبوس', 'مقلوبة', 'صالونة'], 'prices': [],
     'desc': 'دجاج مع الرز اللي تختاره: أبيض، برياني، مجبوس، مندي، أو زربيان.'},
  ]},
  {'id': 'sandwiches', 'name': 'السندويجات والسمبوسة', 'intro': 'خبز إماراتي طازج، وسمبوسة بأربع حشوات.', 'items': [
    {'id': 'khameer', 'name': 'خمير', 'img': 'sand-01', 'prices': [['الحبة', '3.10']], 'desc': 'خبز خمير إماراتي بالهيل والزعفران.'},
    {'id': 'paratha', 'name': 'براتا', 'img': 'sand-02', 'prices': [['الحبة', '2.10']], 'desc': 'براتا طرية.'},
    {'id': 'raqaq', 'name': 'رقاق', 'img': 'sand-03', 'prices': [['الحبة', '2.10']], 'desc': 'خبز رقاق رقيق.'},
    {'id': 'jabab', 'name': 'جباب', 'img': 'sand-04', 'prices': [['الحبة', '2.10']], 'desc': 'خبز جباب، يتقدم مع العسل.'},
    {'id': 'samosa', 'name': 'سمبوسة', 'img': 'sw-02', 'options': ['خضار', 'دجاج', 'لحم', 'جبن'], 'prices': [['الحبة', 2]], 'desc': 'سمبوسة مقرمشة بأربع حشوات.'},
  ]},
  {'id': 'sweets', 'name': 'اللقيمات والحلويات', 'intro': 'لقيمات عادية أو بالحشوة، وحلويات باردة.', 'items': [
    {'id': 'luqaimat', 'name': 'لقيمات', 'img': 'lq-02', 'prices': [['صغير', 11], ['وسط', 22], ['كبير', 43]], 'desc': 'لقيمات مقرمشة بالدبس أو العسل.'},
    {'id': 'luqaimat-filled', 'name': 'لقيمات بالحشوة', 'img': 'lq-01', 'options': ['جبن', 'نوتيلا', 'لوتس', 'بيستاشيو', 'ميكس'], 'prices': [['صغير', 22], ['وسط', 32], ['كبير', 53]], 'desc': 'لقيمات محشية بالنكهة اللي تختارها.'},
    {'id': 'rice-pudding', 'name': 'أرز بالحليب', 'img': 'sweet-01', 'prices': [['الكوب', '10.5']], 'desc': 'أرز بالحليب بارد.'},
    {'id': 'custard', 'name': 'كاسترد', 'img': 'sweet-02', 'prices': [['الكوب', '10.5']], 'desc': 'كاسترد بارد بجوز الهند.'},
    {'id': 'muhallabia', 'name': 'مهلبية', 'img': 'sweet-03', 'prices': [['الكوب', '10.5']], 'desc': 'مهلبية بالزعفران والفستق.'},
    {'id': 'umm-ali', 'name': 'أم علي', 'img': 'sweet-04', 'prices': [['الصحن', '15.75']], 'desc': 'أم علي بالمكسرات.'},
  ]},
]

AR = str.maketrans('0123456789.', '٠١٢٣٤٥٦٧٨٩٫')
def ar(n):
    return str(n).translate(AR)

def webp(name, size):
    im = Image.open(os.path.join(IMG, name + '.jpg')).convert('RGB')
    w, h = im.size; m = min(w, h)
    im = im.crop(((w - m) // 2, (h - m) // 2, (w - m) // 2 + m, (h - m) // 2 + m)).resize((size, size), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'WEBP', quality=54, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()

def wa(text): return 'https://wa.me/%s?text=%s' % (CONTACT['whatsapp'], urllib.parse.quote(text))

images = {}
for cat in MENU:
    for it in cat['items']:
        images.setdefault(it['img'], webp(it['img'], 400))
for extra in ['home-01', 'home-06', 'home-07']:
    images.setdefault(extra, webp(extra, 400))

data = {'menu': MENU, 'contact': CONTACT}
for cat in data['menu']:
    for it in cat['items']:
        it['prices_ar'] = [[n, ar(p)] for n, p in it['prices']]

html = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
html = html.replace('/*DATA*/', 'const DATA=' + json.dumps(data, ensure_ascii=False) + ';\nconst IMGS=' + json.dumps(images) + ';')
html = html.replace('{{WA_ORDER}}', wa('السلام عليكم، أبي أطلب من مرطبات الشامخة'))
html = html.replace('{{WA_EVENT}}', wa('السلام عليكم، أبي أستفسر عن بوفيه وذبائح لمناسبة'))
for k, v in CONTACT.items(): html = html.replace('{{%s}}' % k, v)
open(os.path.join(HERE, 'index.html'), 'w', encoding='utf-8').write(html)
print('index.html', os.path.getsize(os.path.join(HERE, 'index.html')) // 1024, 'KB,', sum(len(c['items']) for c in MENU), 'items,', len(images), 'images')
