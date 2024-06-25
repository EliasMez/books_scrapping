# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookItem(scrapy.Item):
    title = scrapy.Field()
    image = scrapy.Field()
    description = scrapy.Field()
    UPC = scrapy.Field()
    product_type = scrapy.Field()
    price = scrapy.Field()
    price_tax = scrapy.Field()
    tax = scrapy.Field()
    availability = scrapy.Field()
    number_of_reviews = scrapy.Field()


    