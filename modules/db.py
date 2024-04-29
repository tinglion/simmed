import json
from datetime import datetime

import mysql.connector
from peewee import *
from playhouse.shortcuts import ReconnectMixin

from conf import db_conf


class ReconnectMySQLDatabase(ReconnectMixin, MySQLDatabase):
    pass


db_conn_med_ss = ReconnectMySQLDatabase(
    host=db_conf["host"],
    port=db_conf["port"],
    user=db_conf["username"],
    password=db_conf["password"],
    database=db_conf["database"],
)


class JSONField(TextField):
    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        if value is not None:
            return json.loads(value)


class BaseModel(Model):
    create_time = DateTimeField(default=datetime.now)

    class Meta:
        database = db_conn_med_ss

    def commit(self):
        db_conn_med_ss.commit()


class BaseModelNoCreateTime(Model):
    class Meta:
        database = db_conn_med_ss
        timestamps = False

    def commit(self):
        db_conn_med_ss.commit()


class adv_reaction(BaseModelNoCreateTime):
    id = IntegerField()
    name = CharField()
    name_en = CharField()


class adv_vigi_soc_reaction(BaseModelNoCreateTime):
    name_en = CharField()
    reaction_id = IntegerField()
