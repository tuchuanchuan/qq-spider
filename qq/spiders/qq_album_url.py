# coding: utf-8

import logging
import json

import pymysql
import scrapy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from qq.models import TencentArtist, TencentTable

engine = create_engine("mysql+pymysql://root:root@192.168.0.13:3306/albums_from_web?charset=utf8")


class TencentAlbum(scrapy.Spider):
    name = "TencentAlbum"
    # custom_settings = {"DOWNLOAD_DELAY": 0.5}
    album_url = "https://y.qq.com/n/yqq/album/{}.html"
    singer_album_url = "https://c.y.qq.com/v8/fcg-bin/fcg_v8_singer_album.fcg?g_tk=5381&loginUin=2403635410&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&singermid={}&order=time&begin=0&num=133&exstatus=1"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    }

    def start_requests(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        artists = session.query(TencentArtist.artist_mid).all()
        session.close()
        for artist in artists[400000:]:
            Session = sessionmaker(bind=engine)
            session = Session()
            if_exist = session.query(TencentTable).filter(TencentTable.artist_mid == artist).first()
            session.close()
            if if_exist:
                continue
            album_url = self.singer_album_url.format(artist)
            yield scrapy.Request(album_url, headers=self.headers, callback=self.parse, meta=dict(artist_mid=artist))

    def parse(self, response):
        artist_mid = response.meta["artist_mid"]
        json_response = json.loads(response.body)
        code = json_response["code"]
        if code != 0:
            raise Exception
        album_list = json_response["data"]["list"]
        for album in album_list:
            album_mid = album["albumMID"]
            aurl = self.album_url.format(album_mid)
            name = album["albumName"]
            album_id = album["albumID"]
            artist_name = album["singerName"]
            listen_count = album["listen_count"]
            release_company = album["company"]
            Session = sessionmaker(bind=engine)
            session = Session()
            if_exist = session.query(TencentTable).filter(TencentTable.album_id==album_id).first()
            if if_exist:
                session.close()
                continue
            aalbum = TencentTable(url=aurl, name=name, album_id=album_id, artist_name=artist_name, listen_count=listen_count, release_company=release_company)
            session.add(aalbum)
            session.commit()
            session.close()

