# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HouseItem(scrapy.Item):
    price = scrapy.Field()
    address = scrapy.Field()
    neighborhood = scrapy.Field()
    city = scrapy.Field()
    phone_number = scrapy.Field()
    principal_characteristics = scrapy.Field()
    longitude = scrapy.Field()
    latitude = scrapy.Field()
    residence_type = scrapy.Field()
    jurisdiction = scrapy.Field()
    postal_code = scrapy.Field()
    full_description = scrapy.Field()
    main_characteristics = scrapy.Field()
    amenities = scrapy.Field()
    rooms_descriptions = scrapy.Field()
    sold_date = scrapy.Field()
    sold_time = scrapy.Field()
    saved_amound = scrapy.Field()
    date_posted = scrapy.Field()
    sq_feet = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    visit = scrapy.Field()
