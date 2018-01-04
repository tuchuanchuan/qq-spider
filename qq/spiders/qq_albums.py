# coding: utf-8

import json
import logging

import pymysql
import scrapy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from qq.models import TencentGetAlbum

engine = create_engine("mysql+pymysql://root:root@192.168.0.13:3306/albums_from_web?charset=utf8")


class TencentGetAlbumSpider(scrapy.Spider):
    name = "GetAlbum"

    album_url = "https://c.y.qq.com/v8/fcg-bin/album_library?g_tk=1497668653&loginUin=2403635410&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&cmd=firstpage&page={}&pagesize=50&sort=1&language=-1&genre=0&year=1&pay=0&type=-1&company=-1"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    }

    def start_requests(self):
        # for i in range(350, 20677):
        for i in range(2191, 22000):
            url = self.album_url.format(str(i))
            yield scrapy.Request(url, callback=self.parse, headers=self.headers, meta=dict(page=i), dont_filter=True)

    def parse(self, response):
        page = response.meta["page"]
        json_response = json.loads(response.body)
        code = json_response["code"]
        if code != 0:
            raise Exception
        albumList = json_response["data"]["albumlist"]
        Session = sessionmaker(bind=engine)
        session = Session()
        for album in albumList:
            album_mid = album["album_mid"]
            exist = session.query(TencentGetAlbum).filter(TencentGetAlbum.album_mid==album_mid).first()
            if exist:
                session.execute('''update tencent_albums set release_date = :release_date where url = :url''', dict(release_date=album['public_time'], url='https://y.qq.com/n/yqq/album/{}.html'.format(album['album_mid'])))
                exist.release_date = album['public_time']
                logging.info('''update tencent_albums set release_date = {} where url = {}'''.format(album['public_time'], 'https://y.qq.com/n/yqq/album/{}.html'.format(album['album_mid'])))
            else:
                aalbum = TencentGetAlbum(album_mid=album_mid, page=page, release_date=album['public_time'])
                session.add(aalbum)
        session.commit()
        session.close()
