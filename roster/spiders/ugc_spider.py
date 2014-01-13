from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from roster.items import RosterItem

class UgcSpider(CrawlSpider):
    name = 'ugc'
    allowed_domains = ['ugcleague.com']
    start_urls = ['http://ugcleague.com/rankings_tf2h_currentseason.cfm?division=91']
    rules = [
        Rule(SgmlLinkExtractor(allow=('team_page\.cfm',)), callback='parse_roster')
    ]

    def parse_roster(self, response):
        sel = Selector(response)
        roster = RosterItem()
        abbv, name = sel.xpath('//h2/text()')[0].extract().split(u'  \xa0\xa0 ')
        roster['abbreviation'] = abbv
        roster['name'] = name
        roster['url'] = response.url
        roster['ready'] = u'label-success' in sel.xpath('//span[contains(@class, "label")]/@class')[0].extract()
        players_sel = sel.xpath('//table[contains(@class, "table table-rounded")]/tr')
        players = []
        for player_sel in players_sel:
            player = {}
            name = player_sel.xpath('td').xpath('h4/b/text()')[0].extract().strip()
            steam_id = player_sel.xpath('td')[1].xpath('small/b/text()')[0].extract()
            leader = player_sel.xpath('td')[2].xpath('span/text()')[0].extract().strip()
            player['name'] = name
            player['steam_id'] = steam_id
            player['leader'] = leader == u'Leader'
            players.append(player)
        roster['players'] = players
        return roster
