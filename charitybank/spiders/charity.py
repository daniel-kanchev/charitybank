import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from charitybank.items import Article


class CharitySpider(scrapy.Spider):
    name = 'charity'
    start_urls = ['https://charitybank.org/news']

    def parse(self, response):
        links = response.xpath('//h2[@class="blog__item__title"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//li[@class="pagination__item pagination__item--next"]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1[@itemprop="name"]/text()').get().strip()
        date = response.xpath('//span[@class="post__posted-date"]/text()').get()
        if date:
            date = datetime.strptime(date, '%b %d, %Y')
            date = date.strftime('%Y/%m/%d')
        category = response.xpath('//span[@class="post__category"]/text()').getall()
        if category:
            category = ", ".join(category)

        content = response.xpath('//div[@class="post__content"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('category', category)

        return item.load_item()
