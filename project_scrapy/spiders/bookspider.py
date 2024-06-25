from typing import Iterable
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import BookItem
from scrapy.exceptions import CloseSpider
import scrapy
import uuid



class BookSpider(CrawlSpider):
    name = 'bookspider'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['https://books.toscrape.com/']
    # user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    limit = 2
    lang = 'en'
    session_id = str(uuid.uuid4())
    sops_job_name = "JobTest"
    rules = [
        Rule(LinkExtractor(restrict_xpaths="//article/h3/a"), callback='parse', follow=False),
        Rule(LinkExtractor(restrict_xpaths="//li[@class='next']/a"), follow=True)
    ]

    custom_settings = {
    'FEED_EXPORT_FIELDS': ["title",'image','description','UPC','product_type','price','price_tax','tax','availability','number_of_reviews'],
    }

# scrapysplash

    def start_requests(self) -> Iterable[Request]:
        for url in self.start_urls:
            yield scrapy.Request(url, 
                                 meta={
                                     'sops_render_js': 'False',
                                     'sops_residential' : False,
                                     'sops_keep_headers': 'False',
                                     'sops_session_number' : False,
                                     'sops_js_scenario' : 'False',
                                     'sops_country': False,
                                     'sops_follow_redirects' : False,
                                     'sops_initial_status_code' : False,
                                     'sops_final_status_code' : False,
                                     'sops_premium' : False,
                                     'sops_optimize_request' : False,
                                     'sops_max_request_cost' : False,
                                     'sops_max_request_cost' : False,
                                     'sops_session_number': self.session_id,
                                     } )

    def parse(self, response):

        # # A décommenter pour limiter le nombre de liens scrappés au nombre défini par l'attribut limit
        # scrape_count = self.crawler.stats.get_value('item_scraped_count', 0)
        # if scrape_count >= self.limit:
        #     raise CloseSpider("Limit Reached")

        book_item = BookItem()
        book_item['title'] =  response.xpath("//h1/text()").get()
        book_item['image'] = response.xpath("//img/@src").get()
        book_item['description'] = response.xpath("//div[@id='product_description']/following-sibling::p/text()").get()
        book_item['availability'] = response.xpath("//table[@class='table table-striped']//tr[th[text()='Availability']]/td[last()]/text()").get()
        generate_xpath = lambda variable: f"//table[@class='table table-striped']//tr[th[text()='{variable}']]/td/text()"
        items = [('UPC','UPC'),('product_type','Product Type'),('price','Price (excl. tax)'),('price_tax','Price (incl. tax)'),('tax','Tax'),('number_of_reviews','Number of reviews')]
        for item in items:
            book_item[item[0]] = response.xpath(generate_xpath(item[1])).get()
        yield book_item
        # yield scrapy.Request(url=get_scrapeops_url('https://books.toscrape.com/'), callback=self.parse)





