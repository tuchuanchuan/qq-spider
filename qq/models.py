# coding: utf-8

import pymysql
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
engine = create_engine("mysql+pymysql://root:root@192.168.0.13:3306/albums_from_web?charset=utf8")


class TencentTable(Base):
    __tablename__ = 'tencent_albums'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    url = Column(String(100), nullable=False, unique=True)
    name = Column(String(1000), nullable=False)
    artist_name = Column(String(1000), nullable=False)
    release_company = Column(String(100))
    release_date = Column(String(10), default='', )
    company_id = Column(Integer)


class TencentCompanyTable(Base):
    __tablename__ = 'tencent_companies'
    id = Column(Integer, primary_key=True)
    company = Column(String(100), nullable=False)
    company_id = Column(Integer, nullable=True)
    album_total = Column(Integer, default=0)
    mv_total = Column(Integer, default=0)
    song_total = Column(Integer, default=0)
    singer_total = Column(Integer, default=0)


# class TencentUrl(Base):
#     __tablename__ = 'tencent_url'
#     id = Column(Integer, primary_key=True)
#     url = Column(String(100), nullable=False, unique=True)
#     artist_mid = Column(String(50), nullable=False)


class TencentArtist(Base):
    __tablename__ = 'tencent_artists'
    id = Column(Integer, primary_key=True)
    artist = Column(String(100), nullable=False)
    artist_id = Column(Integer, nullable=False)
    artist_mid = Column(String(50), nullable=False)
    page = Column(Integer, nullable=False)


class TencentGetAlbum(Base):
    __tablename__ = 'tencent_get_album'
    id = Column(Integer, primary_key=True)
    album_mid = Column(String(100), nullable=False)
    page = Column(Integer, nullable=False)
    release_date = Column(String, default='')

Base.metadata.create_all(engine)
