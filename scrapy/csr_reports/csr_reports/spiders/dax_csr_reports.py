from ..items import CsrReportsItem
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy import Request

class DaxCsrReportsSpider(scrapy.Spider):
    name = 'dax_csr_reports'
    #allowed_domains = ['google.de']
    # start_urls = ['https://www.google.de/search?q=corporate+responsibility+report+'+companies[0]]

    # https://docs.scrapy.org/en/latest/topics/spiders.html#scrapy-spider
    def start_requests(self):
        dax = ['adidas','Allianz ', 'BASF Bayer','BMW','Continental','Covestro','Daimler','Delivery Hero','Deutsche Bank','Deutsche Börse','Deutsche Post',
               'Deutsche Telekom','Deutsche Wohnen','EON','Fresenius Medical Care','Fresenius','HeidelbergCement','Henkel','Infineon','Linde','Merck','MTU Aero Engines',
               'Münchener Rückversicherungs-Gesellschaft','RWE','SAP','Siemens','Siemens Energy','Volkswagen (VW)','Vonovia']
        for company in dax:
            yield scrapy.Request('https://www.google.de/search?q=corporate+responsibility+report+'+company, self.parse)


    def parse(self, response):
        xlink = LinkExtractor()
        # https://stackoverflow.com/questions/2361426/get-the-first-item-from-an-iterable-that-matches-a-condition#2364277
        # get first search result (non-google link)
        link = next(l for l in xlink.extract_links(response) if "google" not in l.url)
        yield Request(url=link.url, callback=self.download_report)
        # for link in xlink.extract_links(response):
        #     print('Found' + link.url)
            # if "google" not in link.url:
            #     print('Found' + link.url)
                #yield Request(url=link.url)

    # https://coderecode.com/download-files-scrapy/#Downloading_Files
    def download_report(self, response):
        from urllib.parse import urlsplit
        if response:
            # https://docs.scrapy.org/en/latest/topics/selectors.html
            download_link = response.xpath('//a[contains(@href, ".pdf")]/@href').get()
            loader = ItemLoader(item=CsrReportsItem(), selector=download_link)
            url = urlsplit(response.url)
            print('Adding filename: ' + url.netloc)
            loader.add_value('file_name', url.netloc)
            item = CsrReportsItem()
            if response.url not in download_link:
                #item['file_url'] = [response.urljoin(download_link)]
                print('Joined url: ' + response.urljoin(download_link))
                # yield item
                loader.add_value('file_urls', response.urljoin(download_link))
            else:
                #item['file_url'] = [download_link]
                print('Download url: ' + download_link)
                #yield item
                loader.add_value('file_urls', download_link)
            yield loader.load_item()

    def get_base_url(url):
        # https://stackoverflow.com/questions/35616434/how-can-i-get-the-base-of-a-url-in-python#35616564
        from urllib.parse import urlsplit
        return urlsplit(url).netloc