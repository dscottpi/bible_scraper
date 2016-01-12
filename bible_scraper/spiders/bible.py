import scrapy
from scrapy.exceptions import CloseSpider
import sys
import json


class BibleSpider(scrapy.Spider):
    name = "bible"
    allowed_domains = ["bible.com"]

    base_link = "http://bible.com"

    # 111 is the code for the version, change the number to get a different version
    start_urls = ["https://www.bible.com/bible/206/gen.2"]
    output = {}

    def join_verse(self, verse):
        return ''.join(verse)

    def get_xpath(self, response, xpath):
        return response.xpath(xpath).extract()

    def get_last_chapter(self, response, index):
        chapter_length = response.xpath('//span[@class="label"]//text()').extract()[index]
        if chapter_length != "#":
            return chapter_length
        else:
            return self.get_last_chapter(response, index-1)

    def parse(self, response):

        '''
        TODO: Get chapter number from site.
        Book name: response.xpath('//a[@id="reader_book"]/text()').extract()
        Chapter:
        '''
        book = response.xpath('//a[@id="reader_book"]/text()').extract()[0]
        if book not in self.output:
            self.output[book] = {}

        chapter = response.xpath('//a[@id="reader_chapter"]/text()').extract()[0]
        if chapter not in self.output[book]:
            self.output[book][chapter] = {}

        chapter_length = self.get_last_chapter(response, -1)

        verse_string= '//span[@class="verse v%s"]/span[@class="content"]/text()'
        for i in range(1, int(chapter_length) + 1):
            extract_string = verse_string % i
            # xpath expression returns the verse in a list.
            verse = self.join_verse(self.get_xpath(response, extract_string))
            self.output[book][chapter][i] = verse

        if book == "Revelation" and chapter == "22":
            with open("WEB.json", 'w+') as test:
                json.dump(self.output, test, indent=4, sort_keys=True)
            raise CloseSpider("End of Bible")
        else:
            next_chapter = self.base_link + response.xpath('//a[@id="reader_next"]/@href').extract()[0]
            yield scrapy.Request(next_chapter, callback=self.parse)
