import json
import itertools
import datetime
from operator import itemgetter
from scrapy.shell import inspect_response
from scrapy.http import Request
from scrapy.spider import BaseSpider
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import Selector
from roster.items import LogItem
from roster.utils import steam_id_to_64

class LogsTfSpider(BaseSpider):
    name = 'logstf'
    allowed_domains = ['logs.tf']

    def __init__(self, rosters_file=None, days_prev=14, *args, **kwargs):
        super(LogsTfSpider, self).__init__(*args, **kwargs)
        self.max_delta = datetime.timedelta(days=days_prev)
        self.rosters = json.load(open(rosters_file))
        self.teams = []
        self.players = {}
        for i, r in enumerate(self.rosters):
            self.teams.append(r['players'])
            for p in r['players']:
                self.players[steam_id_to_64(p['steam_id'])] = i
        self.start_urls = ['http://logs.tf/json_search?player={}'.format(sid) for sid in self.players.keys()]

    def parse_log(self, response):
        #check if actual scrim/match
        #save log
        sel = Selector(response)
        players_sel = sel.xpath('//table[contains(@id, "players")]/tbody/tr')
        if len(players_sel) >= 18:
            teams = {}
            for p_sel in players_sel:
                color = p_sel.xpath('td')[0].xpath('@class')[0].extract()
                s_id64 = int(p_sel.xpath('td/div[contains(@class, "dropdown")]/ul/li')[0].xpath('a/@href')[0].extract()[9:])
                if color not in teams:
                    teams[color] = []
                teams[color].append(s_id64)
            detected_teams = []
            for players in teams.values():
                t_ids = [self.players.get(pid, None) for pid in players]
                counts = {t_id:t_ids.count(t_id) for t_id in set(t_ids) if t_id is not None}
                if counts:
                    team, player_count = max(counts.items(), key=itemgetter(1))
                    print team
                    if player_count > 5:
                        detected_teams.append(team)
                    else:
                        detected_teams.append(None)
                else:
                    detected_teams.append(None)
            if any(detected_teams):
                log = LogItem()
                log['url'] = response.url
                log['teams'] = [self.rosters[i]['name'] if i is not None else None for i in detected_teams]
                return log

    def parse(self, response):
        now = datetime.datetime.utcnow()
        logs = [l for l in json.loads(response.body)['logs'] if now - datetime.datetime.utcfromtimestamp(l['date']) < self.max_delta]
        return [Request('http://logs.tf/{}'.format(l['id']), callback=self.parse_log) for l in logs]
