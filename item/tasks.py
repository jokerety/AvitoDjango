import time
import telegram

from app.celery import app

from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone

from scrapy import signals
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.signalmanager import dispatcher

from twisted.internet import reactor

from item.crawler.crawler.spiders.spider import AvitoSpider
from item.models import Item


bot = telegram.Bot(token=settings.TELEGRAM_TOKEN)


@app.task
def parse_from_catalog():
    def crawler_results(signal, sender, item, response, spider):
        if not Item.objects.filter(external_id=item.get('id')).first():
            Item.objects.create(
                name=item.get('name'),
                url=item.get('url'),
                time=item.get('time'),
                price=item.get('price'),
                external_id=item.get('id')
            )

    dispatcher.connect(crawler_results, signal=signals.item_scraped)

    runner = CrawlerRunner(get_project_settings())
    d = runner.crawl(AvitoSpider)
    d.addBoth(lambda _: reactor.stop())
    reactor.run()


@app.task
def send_to_telegram():
    bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text="Смотрю объявления...", disable_notification=True)
    items = Item.objects.filter(is_send=False).order_by('parsed_at')
    if not items:
        bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text="Нет новых объявлений", disable_notification=True)

    for item in items:
        try:
            message = render_to_string('item.html', {'item': item })
            bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message, parse_mode=telegram.ParseMode.HTML)
            item.is_send = True
            item.save()
            time.sleep(3.5)
        except Exception as e:
            print(f'Error: {e}')


@app.task
def clear_ancient():
    Item.objects.filter(is_send=False, parsed_at__lt=timezone.now() - timezone.timedelta(days=7)).delete()