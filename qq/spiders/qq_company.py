# coding: utf-8

import logging
import json

import pymysql
import scrapy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from qq.models import TencentCompanyTable

engine = create_engine("mysql+pymysql://root:root@192.168.0.13:3306/albums_from_web?charset=utf8")


class TencentCompany(scrapy.Spider):
    name = "TencentCompany"

    company_url = "https://c.y.qq.com/v8/fcg-bin/fcg_company_detail.fcg?g_tk=5381&loginUin=0&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&type=company&companyId={}&is_show=1"
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    }

    def start_requests(self):
        for i in range(88152):
            url = self.company_url.format(str(i))
            yield scrapy.Request(url, headers=self.headers, callback=self.parse, meta=dict(page=i), dont_filter=True)

    def parse(self, response):
        page = response.meta["page"]
        json_response = json.loads(response.body)
        code = json_response["code"]
        if code != 0:
            raise Exception
        company_data = json_response["data"]["company"]
        company = company_data["name"]
        logging.warn("company_name: %s", company)
        album_total = company_data.get("albumTotal", 0)
        mv_total = company_data.get("mvTotal", 0)
        song_total = company_data.get("songTotal", 0)
        singer_total = company_data.get("singerTotal", 0)
        if company:
            Session = sessionmaker(bind=engine)
            session = Session()
            acompany = TencentCompanyTable(company=company, company_id=page, album_total=album_total, mv_total=mv_total, song_total=song_total, singer_total=singer_total)
            session.add(acompany)
            session.commit()
            session.close()



