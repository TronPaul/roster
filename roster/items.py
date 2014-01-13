# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class RosterItem(Item):
    url = Field()
    abbreviation = Field()
    name = Field()
    players = Field()
    ready = Field()
