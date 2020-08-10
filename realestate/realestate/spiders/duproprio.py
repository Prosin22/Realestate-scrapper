import scrapy
from scrapy.http import Request
from ..items import HouseItem
import json as json

DEBUG = True

def get_right_dim(dim):
    if "x" in dim:
        dim1, dim2 = dim.split("x")
        dim = str(int(dim1)*int(dim2))
    return dim

def principal_characteristics(response):
    principal_characteristics = {}
    characteristics = response.xpath("//div[contains(@class, 'listing-main-characteristics__item')]")

    for characteristic in characteristics:
        title = characteristic.xpath(
            ".//span[contains(@class, 'listing-main-characteristics__title')]/text()").extract_first().replace(
            "\n", "").strip()
        number = characteristic.xpath(".//span[contains(@class, 'listing-main-characteristics__number')]/text()").extract_first()
        if number is None:
            number = "True"
        principal_characteristics[title] = number.replace("\n", "").strip()

    return principal_characteristics

def rooms_descriptions(response):

    rooms_descriptions = {}

    rooms = response.xpath("//div[contains(@class, 'listing-rooms-details__table__item-container')]")

    for room in rooms:
        name = room.xpath(
            ".//div[contains(@class, 'listing-rooms-details__table__item--room')]/text()").extract_first().replace(
            "\n", "").strip()
        storey = room.xpath(
            ".//span[contains(@class, 'listing-rooms-details__table__item-text')]/text()").extract_first().replace(
            "\n", "").strip()
        dimension = room.xpath(
            ".//span[contains(@class, 'listing-rooms-details__table__item--dimensions__content')]/text()").extract_first().replace(
            "\n", "").strip()
        floor = room.xpath(
            ".//div[contains(@class, 'listing-rooms-details__table__item--flooring')]/text()").extract()
        rooms_descriptions[name] = {
            "storey": storey,
            "dimension": dimension,
            "floor": floor[1].replace("\n", "").strip()
        }

    return rooms_descriptions

def amenities(response):

    amenities = {}

    keys_amenities = response.xpath(
        "//h4[contains(@class, 'listing-complete-list-characteristics__content__group__title')]/text()").extract()
    elem_amenities = response.xpath(
        "//div[contains(@class, 'listing-complete-list-characteristics__content__group')]/ul")

    for i, key in enumerate(keys_amenities):
        amenities[key] = elem_amenities[i].xpath(".//li/text()").extract()

    return amenities

def main_characteristics(response):

    main_characteristics = {}

    main_characteristics_items = response.xpath(
        "//div[contains(@class, 'listing-list-characteristics__viewport')]/div[contains(@class, 'listing-box__dotted-row')]/div/text()").extract()

    for i in range(int(len(main_characteristics_items) / 2)):
        main_characteristics[main_characteristics_items[2 * i]] = main_characteristics_items[2 * i + 1]

    return main_characteristics

FOR_SALE = True

START_URL_SOLD = ["https://duproprio.com/en/search/list?search=true&is_sold=1&with_builders=1&parent=1&pageNumber=1&sort=-published_at"]
START_URL_FOR_SALE = ["https://duproprio.com/en/search/list?search=true&is_for_sale=1&with_builders=1&parent=1&sort=-published_at"]

FORMAT_URL_SOLD = "https://duproprio.com/en/search/list?search=true&is_sold=1&with_builders=1&parent=1&pageNumber={}&sort=-published_at"
FORMAT_URL_FOR_SALE = "https://duproprio.com/en/search/list?search=true&is_for_sale=1&with_builders=1&parent=1&pageNumber={}&sort=-published_at"

class BuySearchSpider(scrapy.Spider):
    name = "dupropriobuy"

    if FOR_SALE:
        start_urls = START_URL_FOR_SALE
        format_url = FORMAT_URL_FOR_SALE
    else:
        start_urls = START_URL_SOLD
        format_url = FORMAT_URL_SOLD

    page_index = 1
    max_page = 21  # get_max_page

    def parse(self, response):
        houses = response.xpath("//li[contains(@class, 'search-results-listings-list__item')]")

        if self.page_index == 1 and not DEBUG:
            try:
                self.max_page = response.xpath("//li[contains(@class, 'pagination__item')]/text()").extract()[-1]
            except:
                self.max_page = 1

        if self.page_index > self.max_page:
            return

        for house in houses:
            house_link = house.xpath(".//a[contains(@class, 'search-results-listings-list__item-image-link ')]/@href").extract_first()
            self.url = house_link
            try:
                self.sold_time, self.sold_date = house.xpath(".//div[contains(@class, 'search-results-listings-list__item-description__item search-results-listings-list__item-description__sold-i')]/strong/text()").extract_first().split("on")
            except:
                self.sold_time, self.sold_date = "", ""
            self.saved_amound = house.xpath(".//div[contains(@class, 'search-results-listings-list__item-description__item search-results-listings-list__item-description__amount-saved')]/strong/text()").extract_first()
            if house_link:
                yield Request(url=house_link, callback=self.parse_house)
            if DEBUG:
                break

        self.page_index += 1
        yield Request(
            url=self.format_url.format(
                self.page_index), callback=self.parse)

    def parse_house(self, response):
        house = HouseItem()

        house["price"] = response.xpath("//div[contains(@class, 'listing-price__amount')]/text()").extract_first().replace("\n", "").replace("\xa0","").strip()
        house["address"] = response.xpath("//div[contains(@class, 'listing-location__address')]//h1/text()").extract_first()
        house["neighborhood"], house["city"] = [elem.replace("\n", "").strip() for elem in response.xpath("//div[contains(@class, 'listing-location__group-address')]//h2//a/text()").extract()[:2]]

        house["url"] = self.url

        try:
            ref_json = json.loads(
                response.xpath("//script[contains(@type, 'application/ld+json')]/text()").extract()[2])
            house["longitude"] = ref_json["geo"]['longitude']
            house["latitude"] = ref_json["geo"]['latitude']
            house["residence_type"] = ref_json["@type"]
            house["jurisdiction"] = ref_json["address"]["addressRegion"]
            house["postal_code"] = ref_json["address"]["postalCode"]
            house["phone_number"] = ref_json["telephone"]
        except:
            ref_json = json.loads(
                response.xpath("//script[contains(@type, 'application/ld+json')]/text()").extract()[1])
            house["longitude"] = ref_json["geo"]['longitude']
            house["latitude"] = ref_json["geo"]['latitude']
            house["residence_type"] = ref_json["@type"]
            house["jurisdiction"] = ref_json["address"]["addressRegion"]
            house["postal_code"] = ref_json["address"]["postalCode"]
            house["phone_number"] = ref_json["telephone"]

        house["full_description"] = response.xpath("//div[contains(@class, 'listing-owners-comments__description')]//p/text()").extract_first()

        house["main_characteristics"] = main_characteristics(response)

        house["amenities"] = amenities(response)

        house["rooms_descriptions"] = rooms_descriptions(response)

        house["principal_characteristics"] = principal_characteristics(response)

        house["sold_date"] = self.sold_date
        house["sold_time"] = self.sold_time
        house["saved_amound"] = self.saved_amound

        yield house

START_URL_RENT = ["https://duproprio.com/en/rental/search/list?search=true&is_rental=1&parent=1&pageNumber=1&sort=-published_at"]
FORMAL_URL_RENT = "https://duproprio.com/en/rental/search/list?search=true&is_rental=1&parent=1&pageNumber={}&sort=-published_at"

class RentalSearchSpider(scrapy.Spider):
    name = "dupropriorent"

    start_urls = START_URL_RENT
    format_url = FORMAL_URL_RENT

    page_index = 1
    max_page = 8 # get_max_page

    def parse(self, response):

        houses = response.xpath("//li[contains(@class, 'search-results-listings-list__item--rental')]")

        if self.page_index == 1 and not DEBUG:
            try:
                self.max_page = response.xpath("//li[contains(@class, 'pagination__item')]/text()").extract()[-1]
            except:
                pass

        if self.page_index > self.max_page:
            return

        for house in houses:
            house_link = house.xpath(".//a[contains(@class, 'search-results-listings-list__item-image-link ')]/@href").extract_first()
            if house_link:
                yield Request(url=house_link, callback=self.parse_house)

        if DEBUG:
            return 0
        self.page_index += 1
        yield Request(
            url=self.format_url.format(
                self.page_index), callback=self.parse)

    def parse_house(self, response):
        house = HouseItem()

        house["price"] = response.xpath("//div[contains(@class, 'listing-price__amount')]/text()").extract_first().replace("\n", "").replace("\xa0","").strip()

        house["address"] = response.xpath("//div[contains(@class, 'listing-location__address')]//h1/text()").extract_first()
        house["neighborhood"], house["city"] = [elem.replace("\n", "").strip() for elem in response.xpath("//div[contains(@class, 'listing-location__group-address')]//h2//a/text()").extract()[:2]]

        house["url"] = response.url

        try:
            ref_json = json.loads(response.xpath("//script[contains(@type, 'application/ld+json')]/text()").extract()[2])
            house["longitude"] = ref_json["geo"]['longitude']
            house["latitude"] = ref_json["geo"]['latitude']
            house["residence_type"] = ref_json["@type"]
            house["jurisdiction"] = ref_json["address"]["addressRegion"]
            house["postal_code"] = ref_json["address"]["postalCode"]
            house["phone_number"] = ref_json["telephone"]
        except:
            ref_json = json.loads(response.xpath("//script[contains(@type, 'application/ld+json')]/text()").extract()[1])
            house["longitude"] = ref_json["geo"]['longitude']
            house["latitude"] = ref_json["geo"]['latitude']
            house["residence_type"] = ref_json["@type"]
            house["jurisdiction"] = ref_json["address"]["addressRegion"]
            house["postal_code"] = ref_json["address"]["postalCode"]
            house["phone_number"] = ref_json["telephone"]


        house["full_description"] = response.xpath("//div[contains(@class, 'listing-owners-comments__description')]//p/text()").extract_first()

        house["main_characteristics"] = main_characteristics(response)

        house["amenities"] = amenities(response)

        house["rooms_descriptions"] = rooms_descriptions(response)

        house["principal_characteristics"] = principal_characteristics(response)

        yield house


