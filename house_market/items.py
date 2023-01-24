import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join


def square_root(ch):
    return ch.replace("m", 'm'+format('\u00B2'))


class HouseMarketItem(scrapy.Item):
    link = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(output_processor=TakeFirst())
    address = scrapy.Field(output_processor=TakeFirst())
    type = scrapy.Field(output_processor=TakeFirst())
    area = scrapy.Field(input_processor=MapCompose(
        square_root), output_processor=TakeFirst())
    bathroom = scrapy.Field(output_processor=TakeFirst())
    bedroom = scrapy.Field(output_processor=TakeFirst())
    pass
