import json

import requests

import constants as keys
from data_services import mark_out_of_stock
from spiders.spider_modules.base import BaseSpider
from spiders.test_spider import debug_spider
import json
from pprint import pprint
import bs4
import requests
from pprint import pprint


class TrendyolSpider(BaseSpider):
    name = "ty"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, base_domain="trendyol.com")
        self.start_urls = self.get_links_to_crawl()

    @staticmethod
    def get_links_to_crawl():
        # https://api.trendyol.com/websearchgw/api/aggregations/tum--urunler?q=oyuncak-bebek&culture=tr-TR&storefrontId=1&categoryRelevancyEnabled=undefined&priceAggregationType=DYNAMIC_GAUSS

        r = requests.get("https://www.trendyol.com")
        parsed_html = bs4.BeautifulSoup(r.content, 'html.parser')
        navigation_links = dict()
        for menu in parsed_html.findAll("li", class_="tab-link"):
            menu_title = menu.find("a", class_="category-header").text
            for submenu in menu.findAll("a"):
                if submenu.text:
                    navigation_links[menu_title + '_' + submenu.text] = submenu['href']
        pprint(navigation_links)
        return navigation_links


def parse_ty_list(raw_json):
    parsed_json = json.loads(raw_json, strict=False)
    products = parsed_json.get("result", {}).get("products")

    keys = {
        "name",
        "images",
        "installmentCount",
        "url",
        "tax",
        "ratingScore",
        "brand",
        "categoryHierarchy",
        "price",
        "promotions",
        "rushDeliveryDuration",
        "freeCargo",
    }

    for product in products:
        product = {k: v for k, v in product.items() if k in keys}
        pprint(product)
        yield product


def parse_ty_detail(raw_json):
    keys = {
        "name",
        "brand",
        "image",
        "aggregateRating",
        "url",
        "description",
        "review",
        "offers"
    }

    product = json.loads(raw_json, strict=False)
    product = {k: v for k, v in product.items() if k in keys}

    offers = product.get("offers", {}).get("offers")
    product["offers"] = [{k: v for k, v in offer.items() if k in {"price", "seller"}} for offer in offers]

    pprint(product)




def test_ty():
    r = requests.get("https://trendyol.com")
    ty_catagory_link_parser(r.content)

    list_data = """{"isSuccess":true,"statusCode":200,"error":null,"result":{"products":[{"id":34721778,"name":"Unisex Spor Ayakkabı - Roma Basic + - 36957111","images":["/assets/product/media/images/20200127/16/2577869/62058068/1/1_org_zoom.jpg","/assets/product/media/images/20200127/16/2577869/62058068/2/2_org_zoom.jpg","/assets/product/media/images/20200127/16/2577869/62058068/3/3_org_zoom.jpg","/assets/product/media/images/20200127/16/2577869/62058068/4/4_org_zoom.jpg","/assets/product/media/images/20200127/16/2577869/62058068/5/5_org_zoom.jpg","/assets/product/media/images/20200127/16/2577869/62058068/7/7_org_zoom.jpg","/assets/product/media/images/20200127/16/2577869/62058068/8/8_org_zoom.jpg","/assets/product/media/images/20200127/16/2577869/62058068/9/9_org_zoom.jpg"],"brand":{"id":17,"name":"Puma"},"installmentCount":12,"tax":8,"webColor":"3_Beyaz","businessUnit":"Sportswear","ratingScore":{"averageRating":4.839080459770115,"totalCount":87},"showSexualContent":true,"sections":[{"id":"1"},{"id":"2"},{"id":"9"},{"id":"7"},{"id":"22"}],"categoryHierarchy":"Sneaker/Ayakkabı/Spor Ayakkabı","url":"/puma/unisex-spor-ayakkabi-roma-basic-36957111-p-34721778","merchantId":105275,"campaignId":409693,"price":{"sellingPrice":279.9,"originalPrice":409.9,"manipulatedOriginalPrice":279.9,"discountedPrice":279.9,"buyingPrice":0},"promotions":[],"rushDeliveryDuration":0,"freeCargo":true,"margin":0,"campaignName":"Sportive","listingId":"9e3c6d347abc5fe1048f7602241de419","winnerVariant":"44","discountedPriceInfo":""},{"id":34721792,"name":"Puma 37112002 Flex Renew Unisex Günlük Ayakkabı","images":["/assets/product/media/images/20200127/16/2577869/62058161/1/1_org_zoom.jpg","/assets/product/media/images/20200131/14/2682723/62058170/2/2_org_zoom.jpg","/assets/product/media/images/20200131/14/2682723/62058170/3/3_org_zoom.jpg","/assets/product/media/images/20200131/9/2641589/62058161/1/1_org_zoom.jpg","/assets/product/media/images/20200127/16/2577869/62058161/4/4_org_zoom.jpg","/assets/product/media/images/20200127/16/2577869/62058161/3/3_org_zoom.jpg"],"brand":{"id":17,"name":"Puma"},"installmentCount":12,"tax":8,"webColor":"14_Siyah","businessUnit":"Sportswear","ratingScore":{"averageRating":4.873015873015873,"totalCount":126},"showSexualContent":true,"sections":[{"id":"2"},{"id":"22"},{"id":"9"},{"id":"7"}],"categoryHierarchy":"Yürüyüş Ayakkabısı/Ayakkabı/Spor Ayakkabı","url":"/puma/puma-37112002-flex-renew-unisex-gunluk-ayakkabi-p-34721792","merchantId":107465,"campaignId":477303,"price":{"sellingPrice":298.82,"originalPrice":349.9,"manipulatedOriginalPrice":298.82,"discountedPrice":254,"buyingPrice":0},"promotions":[{"id":63768,"name":"Sepette %15 İndirim\t"}],"rushDeliveryDuration":0,"freeCargo":true,"margin":0,"campaignName":"Tekem Spor ","listingId":"22b2c1afcd888ce28ae64da080ae2763","winnerVariant":"37,5","discountedPriceInfo":"Sepette %15 İndirim\t"},{"id":35663931,"name":"Ayakkabı Stadion III 207903-9001","images":["/assets/product/media/images/20200218/11/3057842/63759902/1/1_org_zoom.jpg","/assets/product/media/images/20200218/11/3057842/63759902/2/2_org_zoom.jpg","/assets/product/media/images/20200218/11/3057842/63759902/3/3_org_zoom.jpg","/assets/product/media/images/20200218/11/3057842/63759902/4/4_org_zoom.jpg","/assets/product/media/images/20200218/11/3057842/63759902/5/5_org_zoom.jpg"],"brand":{"id":7770,"name":"HUMMEL"},"installmentCount":12,"tax":8,"webColor":"3_Beyaz","businessUnit":"Sportswear","ratingScore":{"averageRating":4.421568627450981,"totalCount":102},"showSexualContent":true,"sections":[{"id":"1"},{"id":"2"},{"id":"9"},{"id":"7"},{"id":"22"}],"categoryHierarchy":"Sneaker/Ayakkabı/Spor Ayakkabı","url":"/hummel/ayakkabi-stadion-iii-207903-9001-p-35663931","merchantId":117003,"campaignId":462646,"price":{"sellingPrice":203.5,"originalPrice":249.95,"manipulatedOriginalPrice":203.5,"discountedPrice":142.45,"buyingPrice":0},"promotions":[{"id":62411,"name":"Sepette %30 İndirim"}],"rushDeliveryDuration":0,"freeCargo":true,"margin":0,"campaignName":"Hummel - Sepette %30 İndirim","listingId":"b9ec254d1d79c71697f386c31b9349c7","winnerVariant":"40","discountedPriceInfo":"Sepette %30 İndirim"},{"id":3979276,"name":"Erkek Spor Ayakkabı Vs Pace - B74493","images":["/assets/product/media/images/20191106/16/547653/12980769/1/1_org_zoom.jpg","/assets/product/media/images/20191106/16/547653/12980769/2/2_org_zoom.jpg","/assets/product/media/images/20191106/16/547653/12980769/3/3_org_zoom.jpg","/assets/product/media/images/20191106/16/547653/12980769/4/4_org_zoom.jpg","/assets/product/media/images/20191106/16/547653/12980769/5/5_org_zoom.jpg","/assets/product/media/images/20191106/10/507321/12980766/4/4_org_zoom.jpg","/assets/product/media/images/20191106/10/507321/12980766/5/5_org_zoom.jpg"],"brand":{"id":15,"name":"adidas"},"installmentCount":12,"tax":8,"webColor":"8_Lacivert","businessUnit":"Sportswear","ratingScore":{"averageRating":4.6,"totalCount":430},"showSexualContent":true,"sections":[{"id":"2"},{"id":"22"},{"id":"9"},{"id":"7"}],"categoryHierarchy":"Sneaker/Ayakkabı/Spor Ayakkabı","url":"/adidas/erkek-spor-ayakkabi-vs-pace-b74493-p-3979276","merchantId":4586,"campaignId":474546,"price":{"sellingPrice":218.99,"originalPrice":319,"manipulatedOriginalPrice":218.99,"discountedPrice":218.99,"buyingPrice":0},"promotions":[],"rushDeliveryDuration":0,"freeCargo":true,"margin":0,"campaignName":"Dalkılıç Spor","listingId":"b04e8d43bfd73968a16c584dd43be280","winnerVariant":"44 2/3","discountedPriceInfo":""},{"id":5615082,"name":"Erkek Koşu & Antrenman Ayakkabısı Runfalcon - G28971","images":["/Assets/ProductImages/oa/47/5615082/1/4059812858459_1_org_zoom.jpg","/Assets/ProductImages/oa/47/5615082/1/4059812858459_2_org_zoom.jpg","/Assets/ProductImages/oa/47/5615082/1/4059812858459_3_org_zoom.jpg"],"brand":{"id":15,"name":"adidas"},"installmentCount":12,"tax":8,"webColor":"3_Beyaz","businessUnit":"Sportswear","ratingScore":{"averageRating":4.24203821656051,"totalCount":314},"showSexualContent":true,"sections":[{"id":"9"},{"id":"7"},{"id":"2"},{"id":"22"}],"categoryHierarchy":"Ayakkabı/Spor Ayakkabı/Koşu & Antrenman Ayakkabısı","url":"/adidas/erkek-kosu-antrenman-ayakkabisi-runfalcon-g28971-p-5615082","merchantId":350,"campaignId":477792,"price":{"sellingPrice":243.8,"originalPrice":359,"manipulatedOriginalPrice":243.8,"discountedPrice":243.8,"buyingPrice":0},"promotions":[],"rushDeliveryDuration":0,"freeCargo":true,"margin":0,"campaignName":"Barçın Spor","listingId":"b8de991d3ed396e3456f3e61978c2f9e","winnerVariant":"44,5","discountedPriceInfo":""},{"id":3736038,"name":"Siyah Unisex Sneaker OFF.DS","images":["/Assets/ProductImages/oa/102/3736038/1/OFFSYH3232X40_1_org_zoom.jpg","/Assets/ProductImages/oa/102/3736038/1/OFFSYH3232X40_2_org_zoom.jpg","/Assets/ProductImages/oa/102/3736038/1/OFFSYH3232X40_3_org_zoom.jpg","/Assets/ProductImages/oa/102/3736038/1/OFFSYH3232X40_4_org_zoom.jpg"],"brand":{"id":22922,"name":"DARK SEER"},"installmentCount":12,"tax":8,"webColor":"14_Siyah","businessUnit":"Branded Shoes B","ratingScore":{"averageRating":4.205097087378641,"totalCount":824},"showSexualContent":true,"sections":[{"id":"9"},{"id":"7"},{"id":"22"},{"id":"1"},{"id":"2"}],"categoryHierarchy":"Sneaker/Ayakkabı/Spor Ayakkabı","url":"/dark-seer/siyah-unisex-sneaker-off-ds-p-3736038","merchantId":104936,"campaignId":446748,"price":{"sellingPrice":180,"originalPrice":180,"manipulatedOriginalPrice":180,"discountedPrice":126,"buyingPrice":0},"promotions":[{"id":60616,"name":"Sepette %30 İndirim"}],"rushDeliveryDuration":0,"freeCargo":true,"margin":0,"campaignName":"Dark Seer - Çok Satanlar","listingId":"f6d5749ea78af8d7bf4af4ad57080e2a","winnerVariant":"42","discountedPriceInfo":"Sepette %30 İndirim"},{"id":6044873,"name":"Füme Unisex Sneaker TB107-0","images":["/assets/product/images/20687/20043065/1/1_org_zoom.jpg","/assets/product/images/20687/20043065/2/2_org_zoom.jpg","/assets/product/images/20687/20043065/3/3_org_zoom.jpg"],"brand":{"id":15214,"name":"Tonny Black"},"installmentCount":12,"tax":8,"webColor":"4_Gri","businessUnit":"Branded Shoes B","ratingScore":{"averageRating":4.178100263852243,"totalCount":3032},"showSexualContent":true,"sections":[{"id":"2"},{"id":"9"},{"id":"7"},{"id":"22"},{"id":"1"}],"categoryHierarchy":"Sneaker/Ayakkabı/Spor Ayakkabı","url":"/tonny-black/fume-unisex-sneaker-tb107-0-p-6044873","merchantId":106292,"campaignId":409142,"price":{"sellingPrice":169.99,"originalPrice":289,"manipulatedOriginalPrice":169.99,"discountedPrice":110.49,"buyingPrice":0},"promotions":[{"id":60264,"name":"Sepette %35 İndirim"}],"rushDeliveryDuration":0,"freeCargo":true,"margin":0,"campaignName":"Tonny Black - Yeni Sezon","listingId":"b1192788abadb81233f0097f97a8190c","winnerVariant":"36","discountedPriceInfo":"Sepette %35 İndirim"},{"id":2461550,"name":"Erkek Ayakkabı - Summits - 999807 CHAR","images":["/Assets/ProductImages/oa/47/2461550/3/191665945499_5_org_zoom.jpg","/Assets/ProductImages/oa/47/2461550/3/191665945499_1_org_zoom.jpg","/Assets/ProductImages/oa/47/2461550/3/191665945499_2_org_zoom.jpg","/Assets/ProductImages/oa/47/2461550/3/191665945499_3_org_zoom.jpg"],"brand":{"id":8616,"name":"SKECHERS"},"installmentCount":12,"tax":8,"webColor":"4_Gri","businessUnit":"Sportswear","ratingScore":{"averageRating":4.4,"totalCount":15},"showSexualContent":true,"sections":[{"id":"7"},{"id":"2"},{"id":"22"},{"id":"9"}],"categoryHierarchy":"Sneaker/Ayakkabı/Spor Ayakkabı","url":"/skechers/erkek-ayakkabi-summits-999807-char-p-2461550","merchantId":2617,"campaignId":475195,"price":{"sellingPrice":350.35,"originalPrice":539,"manipulatedOriginalPrice":350.35,"discountedPrice":350.35,"buyingPrice":0},"promotions":[],"rushDeliveryDuration":0,"freeCargo":true,"margin":0,"campaignName":"Skechers","listingId":"edaf08b18d9763509d83fa55d0f6b370","winnerVariant":"41","discountedPriceInfo":""},{"id":36866510,"name":"Ares Aqua Erkek Ayakkabı Siyah","images":["/assets/product/media/images/20200313/14/4409989/65566255/1/1_org_zoom.jpg","/assets/product/media/images/20200313/14/4409989/65566255/2/2_org_zoom.jpg","/assets/product/media/images/20200313/14/4409989/65566255/3/3_org_zoom.jpg","/assets/product/media/images/20200313/14/4409989/65566255/4/4_org_zoom.jpg"],"brand":{"id":682,"name":"Slazenger"},"installmentCount":12,"tax":8,"webColor":"14_Siyah","businessUnit":"Sportswear","ratingScore":{"averageRating":4.833333333333333,"totalCount":18},"showSexualContent":true,"sections":[{"id":"22"},{"id":"9"},{"id":"7"},{"id":"2"}],"categoryHierarchy":"Yürüyüş Ayakkabısı/Ayakkabı/Spor Ayakkabı","url":"/slazenger/ares-aqua-erkek-ayakkabi-siyah-p-36866510","merchantId":4662,"campaignId":475197,"price":{"sellingPrice":179.9,"originalPrice":179.9,"manipulatedOriginalPrice":179.9,"discountedPrice":98.95,"buyingPrice":0},"promotions":[{"id":63391,"name":"Sepette %45 İndirim"}],"rushDeliveryDuration":0,"freeCargo":false,"margin":0,"campaignName":"Slazenger Kadın & Erkek & Çocuk Spor Giyim","listingId":"3d399b194fdbc02ec44c961c32210993","winnerVariant":"43","discountedPriceInfo":"Sepette %45 İndirim"},{"id":3269841,"name":"Erkek Spor Ayakkabı -Turin II - 36696203","images":["/assets/product/media/images/20200318/13/4521492/18283917/1/1_org_zoom.jpg","/assets/product/media/images/20200318/13/4521492/18283917/2/2_org_zoom.jpg","/assets/product/media/images/20200318/13/4521492/18283917/3/3_org_zoom.jpg"],"brand":{"id":17,"name":"Puma"},"installmentCount":12,"tax":8,"webColor":"3_Beyaz","businessUnit":"Sportswear","ratingScore":{"averageRating":4.705882352941177,"totalCount":153},"showSexualContent":true,"sections":[{"id":"22"},{"id":"9"},{"id":"7"},{"id":"2"}],"categoryHierarchy":"Yürüyüş Ayakkabısı/Ayakkabı/Spor Ayakkabı","url":"/puma/erkek-spor-ayakkabi-turin-ii-36696203-p-3269841","merchantId":968,"campaignId":475845,"price":{"sellingPrice":194.99,"originalPrice":379.99,"manipulatedOriginalPrice":249.9,"discountedPrice":194.99,"buyingPrice":0},"promotions":[],"rushDeliveryDuration":0,"freeCargo":false,"margin":0,"campaignName":"Puma - Kadın & Erkek Spor Giyim","listingId":"015e6065591400733ef0ad347ec98f7d","winnerVariant":"43","discountedPriceInfo":""},{"id":34144747,"name":"24860 Erkek Spor Ayakkabı","images":["/assets/product/media/images/20191220/15/1702295/61155407/1/1_org_zoom.jpg","/assets/product/media/images/20191220/15/1702295/61155407/2/2_org_zoom.jpg","/assets/product/media/images/20191220/15/1702295/61155407/3/3_org_zoom.jpg"],"brand":{"id":1410,"name":"Jump"},"installmentCount":12,"tax":8,"webColor":"14_Siyah","businessUnit":"Sportswear","ratingScore":{"averageRating":4.317460317460317,"totalCount":63},"showSexualContent":true,"sections":[{"id":"7"},{"id":"2"},{"id":"22"},{"id":"9"}],"categoryHierarchy":"Sneaker/Ayakkabı/Spor Ayakkabı","url":"/jump/24860-erkek-spor-ayakkabi-p-34144747","merchantId":122850,"campaignId":316827,"price":{"sellingPrice":155,"originalPrice":179.9,"manipulatedOriginalPrice":155,"discountedPrice":155,"buyingPrice":0},"promotions":[],"rushDeliveryDuration":0,"freeCargo":true,"margin":0,"campaignName":"Sportswear","listingId":"c0d6d2ebc590bbb9eec493ece96dac13","winnerVariant":"44","discountedPriceInfo":""},{"id":34919518,"name":"Erkek Siyah Basic Mikro Delikli Spor Ayakkabı 12210540","images":["/assets/product/media/images/20200121/15/2341079/62408909/1/1_org_zoom.jpg","/assets/product/media/images/20200121/15/2341079/62408909/2/2_org_zoom.jpg","/assets/product/media/images/20200121/15/2341079/62408909/3/3_org_zoom.jpg","/assets/product/media/images/20200121/15/2341079/62408909/4/4_org_zoom.jpg","/assets/product/media/images/20200121/15/2341079/62408909/5/5_org_zoom.jpg","/assets/product/media/images/20200121/15/2341079/62408909/6/6_org_zoom.jpg"],"brand":{"id":4951,"name":"Pull & Bear"},"installmentCount":12,"tax":8,"webColor":"14_Siyah","businessUnit":"Kadın A","ratingScore":{"averageRating":4.659898477157361,"totalCount":197},"showSexualContent":true,"sections":[{"id":"7"},{"id":"2"},{"id":"22"},{"id":"9"}],"categoryHierarchy":"Sneaker/Ayakkabı/Spor Ayakkabı","url":"/pull-bear/erkek-siyah-basic-mikro-delikli-spor-ayakkabi-12210540-p-34919518","merchantId":112044,"campaignId":457591,"price":{"sellingPrice":129.95,"originalPrice":129.95,"manipulatedOriginalPrice":129.95,"discountedPrice":129.95,"buyingPrice":0},"promotions":[],"rushDeliveryDuration":0,"freeCargo":true,"margin":0,"campaignName":"Pull & Bear - Yeni Sezon","listingId":"541031cd70c6b437995245ffdd63cbed","winnerVariant":"43","discountedPriceInfo":""},{"id":37658799,"name":"Siyah Sneaker 0012marco","images":["/assets/dev/product/media/images/20200328/15/665098/66953742/1/1_org_zoom.jpg","/assets/dev/product/media/images/20200328/15/665098/66953742/2/2_org_zoom.jpg","/assets/dev/product/media/images/20200328/15/665098/66953742/3/3_org_zoom.jpg","/assets/dev/product/media/images/20200328/15/665098/66953742/4/4_org_zoom.jpg","/assets/dev/product/media/images/20200328/15/665098/66953742/5/5_org_zoom.jpg"],"brand":{"id":93397,"name":"Riccon"},"installmentCount":12,"tax":8,"webColor":"14_Siyah","businessUnit":"Branded Shoes B","ratingScore":{"averageRating":4.5,"totalCount":2},"showSexualContent":true,"sections":[{"id":"22"},{"id":"9"},{"id":"7"},{"id":"2"}],"categoryHierarchy":"Sneaker/Ayakkabı/Spor Ayakkabı","url":"/riccon/siyah-sneaker-0012marco-p-37658799","merchantId":122039,"campaignId":449346,"price":{"sellingPrice":184.46,"originalPrice":253.75,"manipulatedOriginalPrice":184.46,"discountedPrice":119.9,"buyingPrice":0},"promotions":[{"id":61067,"name":"Sepette %35 İndirim"}],"rushDeliveryDuration":0,"freeCargo":true,"margin":0,"campaignName":"Ayakkabıda Nisan İndirimleri","listingId":"71bda0a609200412fb0a1ac397776248","winnerVariant":"41","discountedPriceInfo":"Sepette %35 İndirim"},{"id":32398118,"name":"Revolution 5 BQ3204-003 Erkek Spor Ayakkabı","images":["/assets/product/media/images/20191107/18/561903/58228301/1/1_org_zoom.jpg","/assets/product/media/images/20191107/18/561903/58228301/3/3_org_zoom.jpg","/assets/product/media/images/20191107/18/561903/58228301/2/2_org_zoom.jpg","/assets/product/media/images/20191106/16/547514/58228306/3/3_org_zoom.jpg","/assets/product/media/images/20191106/16/547514/58228306/4/4_org_zoom.jpg"],"brand":{"id":1479,"name":"Nike"},"installmentCount":12,"tax":8,"webColor":"3_Beyaz","businessUnit":"Sportswear","ratingScore":{"averageRating":4.476190476190476,"totalCount":42},"showSexualContent":true,"sections":[{"id":"2"},{"id":"22"},{"id":"9"},{"id":"7"}],"categoryHierarchy":"Ayakkabı/Spor Ayakkabı/Koşu & Antrenman Ayakkabısı","url":"/nike/revolution-5-bq3204-003-erkek-spor-ayakkabi-p-32398118","merchantId":111682,"campaignId":475941,"price":{"sellingPrice":299,"originalPrice":299,"manipulatedOriginalPrice":369.9,"discountedPrice":299,"buyingPrice":0},"promotions":[],"rushDeliveryDuration":0,"freeCargo":true,"margin":0,"campaignName":"Kobi Destek","listingId":"6348337f0575af6e48f6ead6bc374d0c","winnerVariant":"44","discountedPriceInfo":""},{"id":37181086,"name":"Sıyah Erkek Sneaker 02AYY600860A100","images":["/ty1/product/media/images/20200402/19/1054114/66105096/2/2_org_zoom.jpg","/ty2/product/media/images/20200402/19/1054114/66105096/1/1_org_zoom.jpg","/ty1/product/media/images/20200402/19/1054114/66105096/3/3_org_zoom.jpg","/ty1/product/media/images/20200402/19/1054114/66105096/4/4_org_zoom.jpg"],"brand":{"id":7658,"name":"Yaya  by Hotiç"},"installmentCount":12,"tax":8,"webColor":"14_Siyah","businessUnit":"Branded Shoes A","ratingScore":{"averageRating":4.6440677966101696,"totalCount":59},"showSexualContent":true,"sections":[{"id":"7"},{"id":"2"},{"id":"22"},{"id":"9"}],"categoryHierarchy":"Sneaker/Ayakkabı/Spor Ayakkabı","url":"/yaya-by-hotic/siyah-erkek-sneaker-02ayy600860a100-p-37181086","merchantId":968,"campaignId":475142,"price":{"sellingPrice":289,"originalPrice":289,"manipulatedOriginalPrice":289,"discountedPrice":173.4,"buyingPrice":0},"promotions":[{"id":63290,"name":"Sepette %40 İndirim"}],"rushDeliveryDuration":0,"freeCargo":true,"margin":0,"campaignName":"Hotiç - Sepette %40 İndirim","listingId":"76febe10518e03d4491981c782101ee1","winnerVariant":"41","discountedPriceInfo":"Sepette %40 İndirim"},{"id":4084078,"name":"Erkek Spor Ayakkabı - Vs Pace - B74494","images":["/assets/product/media/images/20191023/15/465841/56865653/1/1_org_zoom.jpg","/Assets/ProductImages/oa/47/4084078/4/4057284407083_1_org_zoom.jpg","/assets/product/media/images/20191023/15/465841/56865653/2/2_org_zoom.jpg","/assets/product/media/images/20191106/16/547653/17648916/3/3_org_zoom.jpg","/assets/product/media/images/20191023/15/465841/56865653/3/3_org_zoom.jpg","/Assets/ProductImages/oa/47/4084078/4/4057284407083_2_org_zoom.jpg","/assets/product/media/images/20191023/15/465841/56865653/4/4_org_zoom.jpg","/Assets/ProductImages/oa/47/4084078/4/4057284407083_3_org_zoom.jpg","/assets/product/media/images/20191106/16/547653/17648916/4/4_org_zoom.jpg","/assets/product/media/images/20191106/16/547653/17648916/2/2_org_zoom.jpg","/Assets/ProductImages/oa/47/4084078/4/4057284407083_7_org_zoom.jpg","/Assets/ProductImages/oa/47/4084078/4/4057284407083_8_org_zoom.jpg","/Assets/ProductImages/oa/47/4084078/4/4057284407083_9_org_zoom.jpg","/Assets/ProductImages/oa/47/4084078/3/4057284402989_2_org_zoom.jpg"],"brand":{"id":15,"name":"adidas"},"installmentCount":12,"tax":8,"webColor":"14_Siyah","businessUnit":"Sportswear","ratingScore":{"averageRating":4.677857713828937,"totalCount":1251},"showSexualContent":true,"sections":[{"id":"22"},{"id":"9"},{"id":"7"},{"id":"2"}],"categoryHierarchy":"Yürüyüş Ayakkabısı/Ayakkabı/Spor Ayakkabı","url":"/adidas/erkek-spor-ayakkabi-vs-pace-b74494-p-4084078","merchantId":4586,"campaignId":474546,"price":{"sellingPrice":220.11,"originalPrice":319,"manipulatedOriginalPrice":220.11,"discountedPrice":220.11,"buyingPrice":0},"promotions":[],"rushDeliveryDuration":0,"freeCargo":true,"margin":0,"campaignName":"Dalkılıç Spor","listingId":"7c0243d9e6b6a5a53d149d8542eac39a","winnerVariant":"46","discountedPriceInfo":""},{"id":4129195,"name":"Erkek Koşu & Antrenman Ayakkabısı - V Racer 2.0 - BC0106","images":["/Assets/ProductImages/oa/47/4129195/1/4057291368735_1_org_zoom.jpg","/Assets/ProductImages/oa/47/4129195/1/4057291368735_4_org_zoom.jpg","/Assets/ProductImages/oa/47/4129195/1/4057291368735_2_org_zoom.jpg","/Assets/ProductImages/oa/47/4129195/1/4057291368735_3_org_zoom.jpg","/Assets/ProductImages/oa/47/4129195/1/4057291368735_5_org_zoom.jpg","/Assets/ProductImages/oa/47/4129195/1/4057291368735_6_org_zoom.jpg","/Assets/ProductImages/oa/47/4129195/1/4057291368735_7_org_zoom.jpg"],"brand":{"id":15,"name":"adidas"},"installmentCount":12,"tax":8,"webColor":"3_Beyaz","businessUnit":"Sportswear","ratingScore":{"averageRating":4.276595744680851,"totalCount":141},"showSexualContent":true,"sections":[{"id":"22"},{"id":"9"},{"id":"7"},{"id":"2"}],"categoryHierarchy":"Yürüyüş Ayakkabısı/Ayakkabı/Spor Ayakkabı","url":"/adidas/erkek-kosu-antrenman-ayakkabisi-v-racer-2-0-bc0106-p-4129195","merchantId":350,"campaignId":477792,"price":{"sellingPrice":229.9,"originalPrice":359,"manipulatedOriginalPrice":229.9,"discountedPrice":229.9,"buyingPrice":0},"promotions":[],"rushDeliveryDuration":0,"freeCargo":true,"margin":0,"campaignName":"Barçın Spor","listingId":"ee9dec18609660f63cf6de4be04d8adf","winnerVariant":"37 1/3","discountedPriceInfo":""},{"id":35020114,"name":"Erkek Beyaz Renk Detaylı Spor Ayakkabı 12414560","images":["/assets/product/media/images/20200124/10/2435834/62569931/1/1_org_zoom.jpeg","/assets/product/media/images/20200124/10/2435834/62569931/2/2_org_zoom.jpeg","/assets/product/media/images/20200124/10/2435834/62569931/3/3_org_zoom.jpeg","/assets/product/media/images/20200124/10/2435834/62569931/4/4_org_zoom.jpeg","/assets/product/media/images/20200124/10/2435834/62569931/5/5_org_zoom.jpeg"],"brand":{"id":2685,"name":"Bershka"},"installmentCount":12,"tax":8,"webColor":"3_Beyaz","businessUnit":"Kadın A","ratingScore":{"averageRating":4.504643962848297,"totalCount":323},"showSexualContent":true,"sections":[{"id":"7"},{"id":"2"},{"id":"22"},{"id":"9"}],"categoryHierarchy":"Sneaker/Ayakkabı/Spor Ayakkabı","url":"/bershka/erkek-beyaz-renk-detayli-spor-ayakkabi-12414560-p-35020114","merchantId":104961,"campaignId":449944,"price":{"sellingPrice":169.95,"originalPrice":169.95,"manipulatedOriginalPrice":169.95,"discountedPrice":169.95,"buyingPrice":0},"promotions":[],"rushDeliveryDuration":0,"freeCargo":true,"margin":0,"campaignName":"Bershka - Yeni Sezon ","listingId":"db082e8f84f08920ee436098d56a08e2","winnerVariant":"42","discountedPriceInfo":""},{"id":32615211,"name":"BQ3204-002 REVOLUTION 5 Erkek Koşu Ayakkabı","images":["/assets/product/media/images/20191107/18/561903/58751588/1/1_org_zoom.jpg","/assets/product/media/images/20191107/18/561903/58751588/2/2_org_zoom.jpg","/ty2/product/media/images/20200420/15/4108/59058877/1/1_org_zoom.jpg","/ty1/product/media/images/20200420/15/4108/58751588/1/1_org_zoom.jpg","/ty2/product/media/images/20200420/15/4108/58751579/1/1_org_zoom.jpg","/ty1/product/media/images/20200420/15/4108/58751611/1/1_org_zoom.jpg","/ty1/product/media/images/20200420/15/4108/58751549/1/1_org_zoom.jpg","/ty1/product/media/images/20200420/15/4108/58751618/1/1_org_zoom.jpg","/ty2/product/media/images/20200420/15/4108/58751567/1/1_org_zoom.jpg","/ty1/product/media/images/20200420/15/4108/58751601/1/1_org_zoom.jpg","/ty2/product/media/images/20200420/15/4108/59058877/2/2_org_zoom.jpg","/ty1/product/media/images/20200420/15/4108/58751588/2/2_org_zoom.jpg","/ty2/product/media/images/20200420/15/4108/58751579/2/2_org_zoom.jpg","/ty2/product/media/images/20200420/15/4108/58751611/2/2_org_zoom.jpg","/ty1/product/media/images/20200420/15/4108/58751549/2/2_org_zoom.jpg","/ty1/product/media/images/20200420/15/4108/58751618/2/2_org_zoom.jpg","/ty1/product/media/images/20200420/15/4108/58751567/2/2_org_zoom.jpg","/ty1/product/media/images/20200420/15/4108/58751601/2/2_org_zoom.jpg"],"brand":{"id":1479,"name":"Nike"},"installmentCount":12,"tax":8,"webColor":"14_Siyah","businessUnit":"Sportswear","ratingScore":{"averageRating":4.682242990654205,"totalCount":107},"showSexualContent":true,"sections":[{"id":"2"},{"id":"22"},{"id":"9"},{"id":"7"}],"categoryHierarchy":"Yürüyüş Ayakkabısı/Ayakkabı/Spor Ayakkabı","url":"/nike/bq3204-002-revolution-5-erkek-kosu-ayakkabi-p-32615211","merchantId":111682,"campaignId":371243,"price":{"sellingPrice":319.9,"originalPrice":319.9,"manipulatedOriginalPrice":319.9,"discountedPrice":319.9,"buyingPrice":0},"promotions":[],"rushDeliveryDuration":0,"freeCargo":true,"margin":0,"campaignName":"Sportif Yaşam","listingId":"da48c95659378ecc8d2648a1e50b63c5","winnerVariant":"40","discountedPriceInfo":""},{"id":35545031,"name":"Erkek Kahverengi Koordinatlı Spor Ayakkabı 12214541","images":["/assets/product/media/images/20200212/13/2933540/63429399/1/1_org_zoom.jpg","/assets/product/media/images/20200212/13/2933540/63429399/2/2_org_zoom.jpg","/assets/product/media/images/20200212/13/2933540/63429399/3/3_org_zoom.jpg","/assets/product/media/images/20200212/13/2933540/63429399/4/4_org_zoom.jpg","/assets/product/media/images/20200212/13/2933540/63429399/5/5_org_zoom.jpg","/assets/product/media/images/20200212/13/2933540/63429399/6/6_org_zoom.jpg","/assets/product/media/images/20200212/13/2933540/63429399/7/7_org_zoom.jpg"],"brand":{"id":4951,"name":"Pull & Bear"},"installmentCount":12,"tax":8,"webColor":"6_Kahverengi","businessUnit":"Kadın A","ratingScore":{"averageRating":4.694444444444445,"totalCount":72},"showSexualContent":true,"sections":[{"id":"22"},{"id":"9"},{"id":"7"},{"id":"2"}],"categoryHierarchy":"Sneaker/Ayakkabı/Spor Ayakkabı","url":"/pull-bear/erkek-kahverengi-koordinatli-spor-ayakkabi-12214541-p-35545031","merchantId":112044,"campaignId":457591,"price":{"sellingPrice":169.95,"originalPrice":169.95,"manipulatedOriginalPrice":169.95,"discountedPrice":169.95,"buyingPrice":0},"promotions":[],"rushDeliveryDuration":0,"freeCargo":true,"margin":0,"campaignName":"Pull & Bear - Yeni Sezon","listingId":"de641fc3de51e184b6aa5e2b2a091011","winnerVariant":"42","discountedPriceInfo":""},{"id":36795777,"name":"HMLSTADIL 3.0 CANVAS LIFESTYLE SHOES","images":["/assets/product/media/images/20200311/11/4350575/65426038/1/1_org_zoom.jpg","/assets/product/media/images/20200311/11/4350575/65426038/2/2_org_zoom.jpg","/assets/product/media/images/20200311/11/4350575/65426038/3/3_org_zoom.jpg","/assets/product/media/images/20200311/11/4350575/65426038/4/4_org_zoom.jpg","/assets/product/media/images/20200311/11/4350575/65426038/5/5_org_zoom.jpg","/assets/product/media/images/20200311/11/4350575/65426038/6/6_org_zoom.jpg","/assets/product/media/images/20200311/11/4350575/65426038/7/7_org_zoom.jpg","/assets/product/media/images/20200311/11/4350575/65426038/8/8_org_zoom.jpg"],"brand":{"id":7770,"name":"HUMMEL"},"installmentCount":12,"tax":8,"webColor":"14_Siyah","businessUnit":"Sportswear","ratingScore":{"averageRating":4.65,"totalCount":80},"showSexualContent":true,"sections":[{"id":"1"},{"id":"2"},{"id":"9"},{"id":"7"},{"id":"22"}],"categoryHierarchy":"Sneaker/Ayakkabı/Spor Ayakkabı","url":"/hummel/hmlstadil-3-0-canvas-lifestyle-shoes-p-36795777","merchantId":117003,"campaignId":462646,"price":{"sellingPrice":269.95,"originalPrice":269.95,"manipulatedOriginalPrice":269.95,"discountedPrice":188.97,"buyingPrice":0},"promotions":[{"id":62411,"name":"Sepette %30 İndirim"}],"rushDeliveryDuration":0,"freeCargo":true,"margin":0,"campaignName":"Hummel - Sepette %30 İndirim","listingId":"b08a07114f33ad50ae73bcc3c637cc22","winnerVariant":"42","discountedPriceInfo":"Sepette %30 İndirim"},{"id":4446623,"name":"Erkek Sports Inspired Spor Ayakkabı - Lite Racer - DB0646","images":["/Assets/ProductImages/oa/47/4446623/1/4059323709202_4_org_zoom.jpg","/Assets/ProductImages/oa/47/4446623/1/4059323709202_3_org_zoom.jpg","/Assets/ProductImages/oa/47/4446623/1/4059323709202_1_org_zoom.jpg","/Assets/ProductImages/oa/47/4446623/1/4059323709202_2_org_zoom.jpg"],"brand":{"id":15,"name":"adidas"},"installmentCount":12,"tax":8,"webColor":"3_Beyaz","businessUnit":"Sportswear","ratingScore":{"averageRating":4.411764705882353,"totalCount":34},"showSexualContent":true,"sections":[{"id":"9"},{"id":"7"},{"id":"2"},{"id":"22"}],"categoryHierarchy":"Ayakkabı/Spor Ayakkabı/Koşu & Antrenman Ayakkabısı","url":"/adidas/erkek-sports-inspired-spor-ayakkabi-lite-racer-db0646-p-4446623","merchantId":350,"campaignId":477792,"price":{"sellingPrice":229.9,"originalPrice":359,"manipulatedOriginalPrice":259.2,"discountedPrice":229.9,"buyingPrice":0},"promotions":[],"rushDeliveryDuration":0,"freeCargo":true,"margin":0,"campaignName":"Barçın Spor","listingId":"e0cc70ceb8b523f98af504996251b8ac","winnerVariant":"44 2/3","discountedPriceInfo":""},{"id":4929912,"name":"Beyaz Sneaker 000000000100248650","images":["/assets/product/media/images/20200306/16/4060830/12422295/1/1_org_zoom.jpeg","/Assets/ProductImages/oa/47/4929912/1/8681564871989_2_org_zoom.jpg","/assets/product/media/images/20200306/16/4060830/12422295/2/2_org_zoom.jpeg","/Assets/ProductImages/oa/47/4929912/1/8681564871989_1_org_zoom.jpg","/assets/product/media/images/20200306/16/4060830/12422295/3/3_org_zoom.jpeg","/Assets/ProductImages/oa/47/4929912/1/8681564871989_3_org_zoom.jpg","/assets/product/media/images/20200306/16/4060830/12422295/4/4_org_zoom.jpeg","/Assets/ProductImages/oa/47/4929912/1/8681564871989_4_org_zoom.jpg"],"brand":{"id":19,"name":"U.S. Polo Assn."},"installmentCount":12,"tax":8,"webColor":"3_Beyaz","businessUnit":"GAS Casual","ratingScore":{"averageRating":4.537190082644628,"totalCount":121},"showSexualContent":true,"sections":[{"id":"1"},{"id":"2"},{"id":"9"},{"id":"7"},{"id":"22"}],"categoryHierarchy":"Sneaker/Ayakkabı/Spor Ayakkabı","url":"/u-s-polo-assn/beyaz-sneaker-000000000100248650-p-4929912","merchantId":119791,"campaignId":316829,"price":{"sellingPrice":99.99,"originalPrice":134.99,"manipulatedOriginalPrice":99.99,"discountedPrice":99.99,"buyingPrice":0},"promotions":[],"rushDeliveryDuration":0,"freeCargo":true,"margin":0,"campaignName":"GAS Casual","listingId":"819e6f952f9088867e01b9a81dcccee7","winnerVariant":"45","discountedPriceInfo":""},{"id":6044876,"name":"Beyaz Unisex Sneaker TB107-0","images":["/assets/product/media/images/20191001/11/276158/20043063/1/1_org_zoom.jpg","/assets/product/media/images/20191001/11/276158/20043063/2/2_org_zoom.jpg","/assets/product/media/images/20191001/11/276158/20043063/3/3_org_zoom.jpg"],"brand":{"id":15214,"name":"Tonny Black"},"installmentCount":12,"tax":8,"webColor":"3_Beyaz","businessUnit":"Branded Shoes B","ratingScore":{"averageRating":4.28346709470305,"totalCount":3115},"showSexualContent":true,"sections":[{"id":"9"},{"id":"7"},{"id":"22"},{"id":"1"},{"id":"2"}],"categoryHierarchy":"Sneaker/Ayakkabı/Spor Ayakkabı","url":"/tonny-black/beyaz-unisex-sneaker-tb107-0-p-6044876","merchantId":106292,"campaignId":409142,"price":{"sellingPrice":169.99,"originalPrice":289,"manipulatedOriginalPrice":169.99,"discountedPrice":110.49,"buyingPrice":0},"promotions":[{"id":60264,"name":"Sepette %35 İndirim"}],"rushDeliveryDuration":0,"freeCargo":true,"margin":0,"campaignName":"Tonny Black - Yeni Sezon","listingId":"fb17b3653636d2cd80add47067f4adf7","winnerVariant":"41","discountedPriceInfo":"Sepette %35 İndirim"}],"totalCount":34117,"searchStrategy":"DEFAULT","uxLayout":"Fashion","queryTerm":"","pageIndex":2},"headers":{}}"""

    detailed_data = """{ "@context": "https://schema.org/", "@type": "Product", "color": "no color", "sku": "9560554" ,"gtin13": "3600531230906", "url": "https://www.trendyol.com/maybelline-new-york/kivrim-ve-hacim-etkili-ekstra-siyah-maskara-lash-sensational-intense-black-mascara-3600531230906-p-1263063", "name": "Kıvrım ve Hacim Etkili Ekstra Siyah Maskara - Lash Sensational Intense Black Mascara 3600531230906", "image": ["https://cdn.dsmcdn.com//assets/product/media/images/20191118/17/615208/9560554/1/1_org_zoom.jpg,https://cdn.dsmcdn.com//Assets/ProductImages/164289-2/3600531230906_1_org_zoom.jpg,https://cdn.dsmcdn.com//Assets/ProductImages/164289-1/3600531230906_2_org_zoom.jpg"], "description": "Trendyol.com sayesinde Maybelline ürününe çok özel indirimlerle sahip olabilecek ve alışveriş alışkanlıklarınızı değiştireceksiniz.", "brand": { "@type": "Thing", "name": "Maybelline" }, "aggregateRating": { "@type": "AggregateRating", "worstRating": "1", "bestRating": "5", "ratingValue": "4.77", "reviewCount": "12332" }, "review":[{ "@type": "Review", "author": "hasret aktaş", "datePublished": "2019-11-04", "description": "bu fiyata bu ürünü bulabilmem gerçekten çok büyük bir tesadüf oldu ayrıca almaya niyetlendiğim hediyeyi göndermeniz de çok özel bir düşünce çok çok tşk ederim 😍🥰👏❤", "reviewRating": { "@type": "Rating", "worstRating": "1", "bestRating": "5", "ratingValue": "5" } } ,{ "@type": "Review", "author": "Hafize Aksoy", "datePublished": "2019-11-24", "description": "Yakın zamanda göz ameliyati olmuş olmama rağmen alerjik bir durum yaratmadı. Kibrikler uzun ve kıvrımlı oluyor beğendim", "reviewRating": { "@type": "Rating", "worstRating": "1", "bestRating": "5", "ratingValue": "5" } } ,{ "@type": "Review", "author": "Busra Aytas", "datePublished": "2020-03-27", "description": "37 iken almıştım yorumlara bakarak çok iyi bişi ummuyordum amaaa efsana bu fiyata resmen harika. sadece bir rütuş yaptım kıvırdı ve ayırdı daha ne olsun kii. alacak kişiler içi rahat olsun 👍", "reviewRating": { "@type": "Rating", "worstRating": "1", "bestRating": "5", "ratingValue": "5" } } ], "offers": { "@type": "AggregateOffer", "lowPrice": "40.95", "highPrice": "40.95", "priceCurrency": "TRY", "offerCount": "1", "offers": [ { "@type": "Offer", "seller": { "@type": "Organization", "name": "SİNKA" }, "price": "40.95", "priceCurrency": "TRY", "itemCondition": "https://schema.org/NewCondition", "availability": "https://schema.org/InStock" } ] } }"""
    parse_ty_list(list_data)
    parse_ty_detail(detailed_data)


if __name__ == "__main__":
    # debug_spider(TrendyolSpider)
    test_ty()
