#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = ''
__author__ = 'changxin'
__mtime__ = '2021/5/31'
"""
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess key'
    SQLALCHEMY_RECORD_QUERIES = True
    FLASKY_DB_QUERY_TIMEOUT = 0.5

    REDIS_HOST = "127.0.0.1"  # redis数据库地址
    REDIS_PORT = 6379  # redis 端口号
    REDIS_DB = 0  # 数据库名
    REDIS_EXPIRE = 60  # redis 过期时间60秒

    UPLOAD_PATH = os.path.join(basedir, "upload")
    UPLOAD_ALGORITHM_PATH = os.path.join(basedir, "upload_algorithm")

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL') or 'mysql+pymysql://root:Aizai2017.@localhost:3306/data_credit?charset=utf8mb4'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir,
    #                                                                                              'test-data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir,
                                                                                                 'test-data-dev.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'TEST_DATABASE_URL') or 'mysql+pymysql://root:p@ssw0rd1@localhost:3306/data_credit?charset=utf8mb4'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
