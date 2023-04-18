from urllib.parse import urlencode

import requests
import scrapy
from chocolatescraper.items import ChocolateProduct
from chocolatescraper.itemloaders import ChocolateProductLoader

API_KEY = "d1f98acb-5f5a-47c8-908c-cd5d5580ed49"

def get_poxy_url(url):
    payload={
        'api_key':API_KEY,
        'url':url
    }
    poxy_url="https://proxy.scrapeops.io/v1/?"+urlencode(payload)
    return poxy_url

class ChocolatespiderSpider(scrapy.Spider):
    name = "chocolatespider"
    allowed_domains = []
    # start_urls = ["https://www.chocolate.co.uk/collections/all"]

    def start_requests(self):
        start_urls = ["https://www.chocolate.co.uk/collections/all"]
        yield scrapy.Request(url=get_poxy_url(start_urls[0]),callback=self.parse)
        return super().start_requests()

    def parse(self, response):
        products = response.css('product-item')
        product_item = ChocolateProduct()
        for product in products:
            chocolate = ChocolateProductLoader(item=ChocolateProduct(), selector=product)
            chocolate.add_css('name', 'a.product-item-meta__title::text')
            chocolate.add_css('price', 'span.price',
                              re='<span class="price">\n              <span class="visually-hidden">Sale price</span>(.*)</span>')
            chocolate.add_css('url', 'div.product-item-meta a::attr(href)')
            yield chocolate.load_item()

        next_page = response.css('a[rel="next"] ::attr(href)').get()
        if next_page is not None:
            next_page_url = 'https://www.chocolate.co.uk' + next_page
            yield response.follow(get_poxy_url(next_page_url), callback=self.parse)
        pass
