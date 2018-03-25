# -*- encoding: utf-8 -*-
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, ImagemapSendMessage
)
from linebot.models.imagemap import (
    BaseSize, ImagemapArea, URIImagemapAction, MessageImagemapAction, ImagemapArea
)
import sys
import os
import urllib.request
import json
from datetime import datetime
import re
import sqlite3

import salmon
import battle_stage
import buki
import command_help


app = Flask(__name__)

# 環境変数からchannel_secret・channel_access_tokenを取得
channel_secret = os.environ['LINE_CHANNEL_SECRET']
channel_access_token = os.environ['LINE_CHANNEL_ACCESS_TOKEN']

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

# dbに接続してブキデータを取得
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dbname = os.path.join(BASE_DIR, "splatoon2.sqlite3")
conn = sqlite3.connect(dbname)
cur = conn.cursor()

# メインブキ(短縮名含む)をすべて取得
cur.execute('select name, name_short1, name_short2, name_short3 from weapons')
res = cur.fetchall()
weapons = [flatten for inner in res for flatten in inner]

# サブブキ(短縮名含む)をすべて取得
cur.execute('select sub, sub_short1, sub_short2, sub_short3 from weapons')
res = cur.fetchall()
subs = [flatten for inner in res for flatten in inner]

# スペシャル(短縮名含む)をすべて取得
cur.execute(
    'select special, special_short1, special_short2, special_short3 from weapons')
res = cur.fetchall()
specials = [flatten for inner in res for flatten in inner]

# ブキのジャンル(短縮名含む)をすべて取得
cur.execute(
    'select genre, genre_short1, genre_short2, genre_short3 from weapons')
res = cur.fetchall()
genres = [flatten for inner in res for flatten in inner]

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    print(text)

    m_league = re.fullmatch(r'(?:リーグマッチ|リグマ)(\d+)(時)?', text)
    m_gachi = re.fullmatch(r'(?:ガチマッチ|ガチマ)(\d+)(時)?', text)
    m_regular = re.fullmatch(r'(?:レギュラーマッチ|ナワバリ)(\d+)(時)?', text)

    if text == 'サーモンラン':
        salmon.salmon(line_bot_api, event)

    elif re.fullmatch(r'レギュラーマッチ|ナワバリ', text):
        rule = "regular"
        battle_stage.get_battle_stage(line_bot_api, event, rule)

    elif re.fullmatch(r'ガチマッチ|ガチマ', text):
        rule = "gachi"
        battle_stage.get_battle_stage(line_bot_api, event, rule)

    elif re.fullmatch(r'リーグマッチ|リグマ', text):
        rule = "league"
        battle_stage.get_battle_stage(line_bot_api, event, rule)

    elif m_league is not None:
        rule = "league"
        battle_stage.get_specified_battle_stage(
            line_bot_api, event, rule, m_league)

    elif m_gachi is not None:
        rule = "gachi"
        battle_stage.get_specified_battle_stage(
            line_bot_api, event, rule, m_gachi)

    elif m_regular is not None:
        rule = "regular"
        battle_stage.get_specified_battle_stage(
            line_bot_api, event, rule, m_regular)

    elif text in weapons:
        # ブキ名からサブスペシャルを取得
        cur.execute(
            'select name, sub, special  from weapons where ? in (name, name_short1, name_short2)', (text, ))
        name, sub, special = cur.fetchall()[0]
        buki.get_subspe(line_bot_api, event, name, sub, special)

    elif text in subs:
        # 短縮名から正式名に変換
        cur.execute(
            'select sub from weapons where ? in (sub, sub_short1, sub_short2, sub_short3)', (text, ))
        sub = cur.fetchall()[0][0]

        # 条件に合うブキ一覧を取得
        cur.execute(
            'select name from weapons where ? in (sub, sub_short1, sub_short2, sub_short3)', (text, ))
        res = cur.fetchall()
        names = [flatten for inner in res for flatten in inner]
        buki.get_weapons(line_bot_api, event, sub, *names)

    elif text in specials:
        # 短縮名から正式名に変換
        cur.execute(
            'select special from weapons where ? in (special, special_short1, special_short2, special_short3)', (text, ))
        special = cur.fetchall()[0][0]

        # 条件に合うブキ一覧を取得
        cur.execute(
            'select name from weapons where ? in (special, special_short1, special_short2, special_short3)', (text, ))
        res = cur.fetchall()
        names = [flatten for inner in res for flatten in inner]
        buki.get_weapons(line_bot_api, event, special, *names)

    elif text in genres:
        # 短縮名から正式名に変換
        cur.execute(
            'select genre from weapons where ? in (genre, genre_short1, genre_short2, genre_short3)', (text, ))
        genre = cur.fetchall()[0][0]

        # 条件に合うブキ一覧を取得
        cur.execute(
            'select name from weapons where ? in (genre, genre_short1, genre_short2, genre_short3)', (text, ))
        res = cur.fetchall()
        names = [flatten for inner in res for flatten in inner]
        buki.get_weapons(line_bot_api, event, genre, *names)

    elif re.fullmatch(r'コマンド', text):
        command_help.command_list(line_bot_api, event)

    elif re.fullmatch(r'ブキランダム|ランダムブキ', text):
        # ランダムでブキを1つ取得
        cur.execute('select name, sub, special  from weapons ORDER BY RANDOM() limit 1')
        name, sub, special = cur.fetchall()[0]
        buki.get_subspe(line_bot_api, event, name, sub, special)

if __name__ == "__main__":
    app.run()
