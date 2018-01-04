# coding: utf-8

import logging
import json

import pymysql
import scrapy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from qq.models import TencentTable, TencentGetAlbum

engine = create_engine("mysql+pymysql://root:root@192.168.0.13:3306/albums_from_web?charset=utf8")


class TencentAlbum(scrapy.Spider):
    name = "TencentAlbumInfo"
    album_url = "https://y.qq.com/n/yqq/album/{}.html"
    album_info_url = "https://c.y.qq.com/v8/fcg-bin/fcg_v8_album_info_cp.fcg?albummid={}&g_tk=5381&loginUin=0&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    }

    def start_requests(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        albums = session.query(TencentGetAlbum).order_by(TencentGetAlbum.id.desc()).all()
        for album in albums:
            if_exist = session.query(TencentTable).filter(TencentTable.url == self.album_url.format(albumalbum_mid)).first()
            if if_exist:
                logging.info("Pass")
                continue
            info_url = self.album_info_url.format(album[0])
            yield scrapy.Request(info_url, headers=self.headers, callback=self.parse, meta=dict(album_mid=album.album_mid, release_date=album.release_date))
        session.close()

    def parse(self, response):
        album_mid = response.meta["album_mid"]
        release_date = response.meta['release_date']
        json_response = json.loads(response.body)
        code = json_response["code"]
        if code != 0:
            raise Exception
        data = json_response["data"]
        name = data["name"]
        artist_name = data["singername"]
        release_company = data["company"]
        url = self.album_url.format(album_mid)
        company_new = data["company_new"]
        if company_new:
            company_id = data["company_new"].get("id", None)
        else:
            company_id = None
        Session = sessionmaker(bind=engine)
        session = Session()
        album = TencentTable(url=url, name=name, artist_name=artist_name, release_company=release_company, company_id=company_id, release_date=release_date)
        session.add(album)
        session.commit()
        session.close()
