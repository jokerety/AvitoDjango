import random

import scrapy

USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux i686; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0 Miveo/4.3",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; ; hostname:ivc2-4; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36"
]

class AvitoSpider(scrapy.Spider):
    name = 'avito_spider'
    allowed_domains = ['avito.ru']
    start_urls = [
        'https://www.avito.ru/rossiya/odezhda_obuv_aksessuary/kupit-aksessuary-ASgBAgICAUTeAtoL?cd=1&f=ASgBAgECAUTeAtoLAUXGmgwaeyJmcm9tIjoxNTAwMCwidG8iOjQwMDAwMH0&q=chanel&s=104'
    ]

    @staticmethod
    def is_chanel(item):
        item_name = item.get('name', '').lower()
        if not item_name:
            return False

        for word in ['chanel', 'шанель', 'шанел', 'channel', 'шанэль', 'shanel']:
            if item_name.find(word) != -1:
                return True
        return False

    @staticmethod
    def is_ancient(item):
        item_time = item.get('time', '').lower()
        if not item_time:
            return False

        for word in ['день', 'дня', 'дней']:
            if item_time.find(word) != -1:
                return True
        return False

    def start_requests(self):
        try:
            for url in self.start_urls:
                print(f'Parse page: {url}')
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    headers={
                        'User-Agent': random.choice(USER_AGENTS)
                    },
                    dont_filter=True,
                )
        except Exception as e:
            print(f'Error: {e}')

    def parse(self, response):
        items = response.xpath('//div[@data-marker="item" and contains(@class, "iva-item-list-H_dpX")]')
        try:
            for item in reversed(items):
                data = {
                    'id': item.xpath('@data-item-id').get(),
                    'url': 'https://www.avito.ru' + item.xpath('.//a[@data-marker="item-title"]/@href').get(),
                    'name': item.xpath('.//h3[@itemprop="name"]/text()').get(),
                    'time': item.xpath('.//div[@data-marker="item-date"]/text()').get(),
                    'price': item.xpath('.//meta[@itemprop="price"]/@content').get(),
                }

                if self.is_chanel(data) and not self.is_ancient(data):
                    yield data

        except Exception as e:
            print(f'Error: {e}')
