# coding: utf-8

import logging
import json

import pymysql
import scrapy
from scrapy.selector import Selector
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from qq.models import TencentArtist


engine = create_engine("mysql+pymysql://root:root@192.168.0.13:3306/albums_from_web?charset=utf8")


class Tencent(scrapy.Spider):
    name = "TencentArtist"
    allowed_domains = ['y.qq.com']
    #start_urls = ['https://y.qq.com/portal/album_lib.html']
    #url_qq = "https://y.qq.com/portal/album_lib.html#t9=1&t8={}&t7=-1&t6=-1&t4=1&t2=-1&t1=1&"
    singer_album_url = "https://c.y.qq.com/v8/fcg-bin/fcg_v8_singer_album.fcg?g_tk=5381&loginUin=2403635410&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&singermid={}&order=time&begin=0&num=30&exstatus=1"
    singer_url = "https://c.y.qq.com/v8/fcg-bin/v8.fcg?channel=singer&page=list&key=all_all_all&pagesize=100&pagenum={}&g_tk=5381&loginUin=2403635410&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    }

    def start_requests(self):
        for i in range(982, 5527):
                if i == 0:
                    url_album = "https://y.qq.com/portal/album_lib.html"
                else:
                    url_album = self.singer_url.format(str(i))
                #logging.warn("URL: %s", url_album)
                yield scrapy.Request(url_album, headers=self.headers, callback=self.parse, meta=dict(page=i), dont_filter=True)

    def parse(self, response):
        page = response.meta["page"]
        json_response = json.loads(response.body)
        code = json_response["code"]
        if code != 0:
            raise Exception
        artists = json_response["data"]["list"]
        logging.warn("Len: %d", len(artists))
        for artist in artists:
            artist_name = artist["Fsinger_name"]
            artist_mid = artist["Fsinger_mid"]
            artist_id = int(artist["Fsinger_id"])
            logging.warn("artist_name: %s", artist_name)
            Session = sessionmaker(bind=engine)
            session = Session()
            if_exist = session.query(TencentArtist).filter(TencentArtist.artist_id==artist_id).first()
            if if_exist:
                session.close()
                continue
            aartist = TencentArtist(artist=artist_name, artist_id=artist_id, artist_mid=artist_mid, page=page)
            session.add(aartist)
            session.commit()
            session.close()
