# Até 2k resultados
# passar url
from house_market.spiders.remax import RemaxBotSpider
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def main():
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(RemaxBotSpider)
    process.start()


if __name__ == '__main__':
    main()
