import scrapy
from scrapy.http import Request
from ..items import HouseItem
import json as json
import re

START_URL_CONDO = ["https://www.kijiji.ca/b-condo-for-sale/canada/c643l0?sort=dateDesc"]
FORMAT_URL_CONDO = "https://www.kijiji.ca/b-condo-for-sale/canada/page-{}/c643l0?sort=dateDesc"

START_URL_HOUSE = ["https://www.kijiji.ca/b-house-for-sale/canada/c35l0?sort=dateDesc"]
FORMAT_URL_HOUSE = "https://www.kijiji.ca/b-house-for-sale/canada/page-{}/c35l0?sort=dateDesc"

BASE_URL = "https://www.kijiji.ca"

DEBUG = False

HOUSE = False

def parse_features(ref_json):
    keys_principal_char = ["Bathrooms", "Bedrooms", "Size (sqft)"]

    principal_characteristics = {}

    amenities = {}

    for attributes in ref_json["adAttributes"]["attributes"]:
        key = attributes["localeSpecificValues"]['en']["label"]
        label = attributes["localeSpecificValues"]['en']["value"]

        if label == None:
            label = attributes['machineValue']

        if key in keys_principal_char:
            principal_characteristics[key] = label
        else:
            amenities[key] = label

    return principal_characteristics, amenities


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

class KijijiBuySpider(scrapy.Spider):

    name = "kijijibuy"

    if HOUSE:
        start_urls = START_URL_HOUSE
        format_url = FORMAT_URL_HOUSE
    else:
        start_urls = START_URL_CONDO
        format_url = FORMAT_URL_CONDO

    page_index = 1
    max_page = 100

    def parse(self, response):
        houses = response.xpath("//div[contains(@class, 'search-item')]")

        if self.page_index > self.max_page:
            return

        for house in houses:
            house_link = BASE_URL + house.xpath(".//a[contains(@class, 'title')]/@href").extract_first()
            self.city = house.xpath(".//div[contains(@class, 'location')]/span/text()").extract_first()
            self.title = house.xpath(".//a[contains(@class, 'title')]/text()").extract_first().replace("\n","").strip()

            if house_link:
                yield Request(url=house_link, callback=self.parse_house)

        self.page_index += 1
        yield Request(url=self.format_url.format(self.page_index), callback=self.parse)

    def parse_house(self, response):
        ref_json = json.loads(response.xpath("//script[contains(@type, 'text/javascript')]/text()").extract()[6].replace("window.__data=","")[:-1])
        ref_json = ref_json["viewItemPage"]["viewItemData"]

        house = HouseItem()

        house["url"] = response.url

        house["price"] = ref_json["gptData"]["gptTargetting"]["price"]

        house["address"] = ref_json["adLocation"]["mapAddress"]
        house["longitude"] = ref_json["adLocation"]["longitude"]
        house["latitude"] = ref_json["adLocation"]["latitude"]
        house["jurisdiction"] = ref_json["adLocation"]["province"]
        house["visit"] = ref_json["visitCounter"]

        house["full_description"] = cleanhtml(ref_json["description"].replace("\n","").strip())

        house["title"] = self.title

        house["city"] = self.city.replace("\n","").strip()
        house["date_posted"] = response.xpath("//div[contains(@class, 'datePosted-')]/time/@datetime").extract_first()

        if HOUSE:
            house["residence_type"] = "House"
        else:
            house["residence_type"] = "Condo"

        house["principal_characteristics"] = parse_features(ref_json)

        yield house


START_URL_RENT = ["https://www.kijiji.ca/b-grand-montreal/5-1-2/k0l80002?sort=dateDesc&dc=true"]
FORMAT_URL_RENT = "https://www.kijiji.ca/b-appartement-condo/grand-montreal/5-1-2/page-{}/k0c37l80002?sort=dateDesc"

class KijijiRentSpider(scrapy.Spider):
    name = "kijijirent"

    start_urls = START_URL_RENT
    format_url = FORMAT_URL_RENT

    page_index = 1
    max_page = 79

    def parse(self, response):
        houses = response.xpath("//div[contains(@class, 'search-item')]")

        if self.page_index > self.max_page:
            return

        for house in houses:
            house_link = BASE_URL + house.xpath(".//a[contains(@class, 'title')]/@href").extract_first()
            self.city = house.xpath(".//div[contains(@class, 'location')]/span/text()").extract_first()
            self.title = house.xpath(".//a[contains(@class, 'title')]/text()").extract_first().replace("\n","").strip()

            if house_link:
                yield Request(url=house_link, callback=self.parse_house)

            if DEBUG:
                break


        self.page_index += 1
        yield Request(url=self.format_url.format(self.page_index), callback=self.parse)

    def parse_house(self, response):
        ref_json = json.loads(
            response.xpath("//script[contains(@type, 'text/javascript')]/text()").extract()[6].replace("window.__data=",
                                                                                                       "")[:-1])
        ref_json = ref_json["viewItemPage"]["viewItemData"]

        house = HouseItem()

        house["url"] = response.url

        house["price"] = ref_json["gptData"]["gptTargetting"]["price"]
        house["title"] = self.title

        house["address"] = ref_json["adLocation"]["mapAddress"]
        house["longitude"] = ref_json["adLocation"]["longitude"]
        house["latitude"] = ref_json["adLocation"]["latitude"]
        house["jurisdiction"] = ref_json["adLocation"]["province"]
        house["visit"] = ref_json["visitCounter"]

        house["full_description"] = cleanhtml(ref_json["description"].replace("\n", "").strip())

        house["city"] = self.city.replace("\n", "").strip()
        house["date_posted"] = response.xpath("//div[contains(@class, 'datePosted-')]/time/@datetime").extract_first()

        if HOUSE:
            house["residence_type"] = "House"
        else:
            house["residence_type"] = "Condo"

        house["principal_characteristics"], house["amenities"] = parse_features(ref_json)

        yield house
