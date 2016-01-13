import scrapy
from scrapy.exceptions import CloseSpider
import sys
import json
import urllib
from threading import Thread


class BibleSpider(scrapy.Spider):
    name = "bible"
    allowed_domains = ["bible.com"]

    base_link = "http://bible.com"

    # 111 is the code for the version, change the number to get a different version
    start_urls = ["https://www.bible.com/bible/206/gen.1"]
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

class BibleMp3Spider(scrapy.Spider):
    name = "bible_mp3"
    allowed_domains = ["bible.com"]

    base_link = "http://bible.com"

    # 111 is the code for the version, change the number to get a different version
    start_urls = ["https://www.bible.com/bible/206/gen.1"]
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

    # Thread function for downloading mp3
    def download_mp3(self, mp3_url, filename):
        urllib.urlretrieve (mp3_url, filename)

    def parse(self, response):
        book = response.xpath('//a[@id="reader_book"]/text()').extract()[0]
        chapter = response.xpath('//a[@id="reader_chapter"]/text()').extract()[0]
        filename = book + chapter + ".mp3"

        #Get mp3 link
        mp3_url = response.xpath('//audio[@id="reader_audio_player"]/@src').extract()[0]
        mp3_url = mp3_url.split("?", 1)[0]
        mp3_url = "http:" + mp3_url

        download_thread = Thread(target = self.download_mp3, args = (mp3_url, filename))
        download_thread.start()

        if book == "Revelation" and chapter == "22":
            raise CloseSpider("End of Bible")
        else:
            next_chapter = self.base_link + response.xpath('//a[@id="reader_next"]/@href').extract()[0]
            yield scrapy.Request(next_chapter, callback=self.parse)
