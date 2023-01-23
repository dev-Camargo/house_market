import scrapy
from scrapy.loader.processors import MapCompose, TakeFirst, Join


def square_root(ch):
    return ch.replace(u"\n", '').replace("2", u'\00B2')


class HouseMarketItem(scrapy.Item):
    area = scrapy.Field(input_processor=MapCompose(square_root),
                        output_processor=TakeFirst()
                        )
    pass
