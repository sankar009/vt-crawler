# -*- coding: utf-8 -*-
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule

from vitrinbot.items import ProductItem
from scrapy.selector import Selector
from vitrinbot.base import utils

removeCurrency = utils.removeCurrency
getCurrency = utils.getCurrency
replaceComma = utils.replaceComma



class MarkaparkSpider(CrawlSpider):
    name = 'markapark'
    allowed_domains = ['markapark.com']
    start_urls = ['http://www.markapark.com/']

    xml_filename = 'markapark-%d.xml'

    xpaths = {

    }

    rules = (
        Rule(LinkExtractor(allow=('catinfo\.asp\?.*cid=\d+'),deny=('catinfo\.asp\?.*brw'))),
        Rule(LinkExtractor(allow=('pinfo\.asp\?.*pid=\d+')), callback='parse_item',)

    )

    def parse_item(self, response):
        i = ProductItem()
        sl = Selector(response=response)
        i['url'] = response.url
        i['id'] = "".join(sl.xpath('//p[@class="UrunBilgisiUrunKodu"]/text()').extract()).strip()
        i['title'] = "".join(sl.xpath('//h1[@class="UrunBilgisiUrunAdi"]/text()').extract()).strip()

        i['brand'] = sl.xpath('//a[@class="KategoriYazdirKategoriLink"]/text()')[0].extract()
        cat = sl.xpath('//tr[@class="KategoriYazdirTabloTr"]//a/text()').extract()
        del(cat[0])
        del(cat[len(cat)-1])
        i['category'] = " > ".join(cat)

        try:
            if sl.xpath('//p[@id="runBilgisiPiyasadaDiv"]'):
                priceText = "".join(sl.xpath('//p[@id="runBilgisiPiyasadaDiv"]/text()').extract())
                # i['price'] = removeCurrency(priceText)
                i['price'] = replaceComma(removeCurrency(priceText))
                specialPriceText = "".join(sl.xpath('//p[@id="UrunBilgisiIndirimsizFiyatiDiv"]/text()').extract())
                # i['special_price'] = removeCurrency(specialPriceText)
                i['special_price'] = replaceComma(removeCurrency(specialPriceText))
            else:
                priceText = "".join(sl.xpath('//p[@id="UrunBilgisiIndirimsizFiyatiDiv"]/text()').extract())
                i['price'] = replaceComma(removeCurrency(priceText))
                i['special_price'] = ''
        except:
            priceText = ''
            self.log("HATA! Url: %s" %response.url)

        i['currency'] = getCurrency(priceText)
        i['sizes'] = sl.xpath('//label[@class="_1"]/text()').extract()

        if not sl.xpath('//td[@class="UrunBilgisiUrunResimSlaytTd"]'):
            i['images'] = "".join(sl.xpath('//a[@class="MagicZoomPlus"]/@href').extract())
        else:
            i['images'] = sl.xpath('//td[@class="UrunBilgisiUrunResimSlaytTd"]//a/@href').extract()

        i['description'] = i['expire_timestamp'] = i['colors'] = ''


        return i
