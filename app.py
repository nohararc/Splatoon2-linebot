# -*- encoding: utf-8 -*-
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, ImagemapSendMessage, MessageAction, QuickReply, QuickReplyButton
)
import sys
import os
import urllib.request
import json
from datetime import datetime
import re
import sqlite3
import random

import salmon
import battle_stage
import buki
import command_help

import logging
from logging import StreamHandler

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

# ブランド名をすべて取得
cur.execute(
    'select brand_name from brand')
res = cur.fetchall()
brands = [flatten for inner in res for flatten in inner]

# ギアパワーの名前(短縮名含む)をすべて取得
cur.execute(
    'select distinct easy_gear_power, easy_gear_power_short1, easy_gear_power_short2, easy_gear_power_short3, hard_gear_power, hard_gear_power_short1, hard_gear_power_short2, hard_gear_power_short3 from brand')
res = cur.fetchall()
gears = [flatten for inner in res for flatten in inner]


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

    app.logger.info(text)
    print(text)

    m_league = re.fullmatch(r'(?:リーグマッチ|リグマ)(\d+)(時)?', text)
    m_gachi = re.fullmatch(r'(?:ガチマッチ|ガチマ)(\d+)(時)?', text)
    m_regular = re.fullmatch(r'(?:レギュラーマッチ|ナワバリ)(\d+)(時)?', text)
    m_random_buki = re.fullmatch(r'(?:ブキランダム|ランダムブキ) (?P<genre>.+)', text)
    m_rule = re.fullmatch(r'(?:次の)(?P<rule>エリア|ホコ|ヤグラ|アサリ)', text)
    m_time_range = re.fullmatch(r'(?P<rule>ガチマッチ|ガチマ|リーグマッチ|リグマ)(?P<hours>\d+(?P<sep>-|～)\d+)', text)

    if re.fullmatch(r'サーモンラン|バイト', text):
        salmon.salmon(line_bot_api, event)

    elif re.fullmatch(r'(サーモンラン|バイト)(次|つぎ)', text):
        salmon.salmon_next(line_bot_api, event)

    elif re.fullmatch(r'レギュラーマッチ|ナワバリ', text):
        rule = "regular"
        battle_stage.get_battle_stage(line_bot_api, event, rule)

    elif re.fullmatch(r'ガチマッチ|ガチマ', text):
        rule = "gachi"
        battle_stage.get_battle_stage(line_bot_api, event, rule)

    elif re.fullmatch(r'リーグマッチ|リグマ', text):
        rule = "league"
        battle_stage.get_battle_stage(line_bot_api, event, rule)

    elif re.fullmatch(r'(レギュラーマッチ|ナワバリ)(オール|一覧|全部|ぜんぶ)', text):
        rule = "regular"
        battle_stage.get_battle_stage_all(line_bot_api, event, rule)

    elif re.fullmatch(r'(ガチマッチ|ガチマ)(オール|一覧|全部|ぜんぶ)', text):
        rule = "gachi"
        battle_stage.get_battle_stage_all(line_bot_api, event, rule)

    elif re.fullmatch(r'(リーグマッチ|リグマ)(オール|一覧|全部|ぜんぶ)', text):
        rule = "league"
        battle_stage.get_battle_stage_all(line_bot_api, event, rule)

    elif m_rule is not None:
        req = urllib.request.Request("https://spla2.yuu26.com/schedule")
        req.add_header("user-agent", "@nohararc")
        with urllib.request.urlopen(req) as res:
            response_body = res.read().decode("utf-8")
            response_json = json.loads(response_body.split("\n")[0])
            data = response_json["result"]

        stage = ["■ガチマッチ"]
        for d in data["gachi"]:
            if "ガチ" + m_rule.group("rule") in d["rule"]:
                start_time = datetime.strptime(d["start"], '%Y-%m-%dT%H:%M:%S')
                stage += [start_time.strftime("%m/%d %H:%M") + " ～", d["maps_ex"][0]["name"], d["maps_ex"][1]["name"], ""]
        stage += ["■リーグマッチ"]
        for d in data["league"]:
            if "ガチ" + m_rule.group("rule") in d["rule"]:
                start_time = datetime.strptime(d["start"], '%Y-%m-%dT%H:%M:%S')
                stage += [start_time.strftime("%m/%d %H:%M") + " ～", d["maps_ex"][0]["name"], d["maps_ex"][1]["name"], ""]
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text="{stage}".format(stage="\n".join(stage)[:-1]))
            ]
        )

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
            'select name from weapons where ? in (sub, sub_short1, sub_short2, sub_short3)', (sub, ))
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
            'select name from weapons where ? in (special, special_short1, special_short2, special_short3)', (special, ))
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
        cur.execute(
            'select name, sub, special from weapons ORDER BY RANDOM() limit 1')
        name, sub, special = cur.fetchall()[0]
        buki.get_subspe(line_bot_api, event, name, sub, special)

    elif m_random_buki:
        # ランダムでブキを1つ取得(ブキのジャンル指定)
        cur.execute(
            'select name, sub, special from weapons where genre=? order by random() limit 1', (m_random_buki.group("genre"), ))
        try:
            name, sub, special = cur.fetchall()[0]
            buki.get_subspe(line_bot_api, event, name, sub, special)
        except:
            pass

    elif re.fullmatch(r'ステージランダム|ランダムステージ', text):
        # ランダムでステージを1つ取得
        cur.execute('select stage_name from stages order by random() limit 1')
        stage_name = cur.fetchall()[0][0]
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text="{stage}".format(stage=stage_name))
            ]
        )

    elif re.fullmatch(r'ルールランダム|ランダムルール', text):
        # ランダムでルールを1つ取得
        rules = ["ガチアサリ", "ガチヤグラ", "ガチホコバトル", "ガチエリア", "ナワバリ"]
        rule_name = random.choice(rules)
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text="{rule}".format(rule=rule_name))
            ]
        )

    elif re.fullmatch(r'ガチルールランダム|ランダムガチルール', text):
        # ランダムでルールを1つ取得
        rules = ["ガチアサリ", "ガチヤグラ", "ガチホコ", "ガチエリア"]
        rule_name = random.choice(rules)
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text="{rule}".format(rule=rule_name))
            ]
        )

    elif text in brands:
        # ブランド名から付きやすい/付きにくいギアパワーを取得
        cur.execute(
            'select easy_gear_power, hard_gear_power from brand where brand_name=?', (text, ))
        gear_power = cur.fetchall()
        easy_gear_power, hard_gear_power = gear_power[0][0], gear_power[0][1]
        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(
                    text="ブランド: {text}\n付きやすい: {easy}\n付きにくい: {hard}".format(text=text, easy=easy_gear_power, hard=hard_gear_power))
            ]
        )

    elif text in gears:
        # ギアパワーから、付きやすい/付きにくいブランドを取得

        # 短縮名から正式名を取得
        cur.execute(
            'select easy_gear_power from brand where ? in (easy_gear_power, easy_gear_power_short1, easy_gear_power_short2, easy_gear_power_short3)', (text, ))
        gear_power = cur.fetchall()[0][0]

        # ギアパワーから、付きやすいブランドを取得
        cur.execute(
            'select brand_name from brand where easy_gear_power = ?', (gear_power, ))
        res = cur.fetchall()
        easy_brand_names = [flatten for inner in res for flatten in inner]
        easy_brand_names = ", ".join(easy_brand_names)

        # ギアパワーから、付きにくいブランドを取得
        cur.execute(
            'select brand_name from brand where hard_gear_power = ?', (gear_power, ))
        res = cur.fetchall()
        hard_brand_names = [flatten for inner in res for flatten in inner]
        hard_brand_names = ", ".join(hard_brand_names)

        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(
                    text="ギア: {text}\n付きやすい: {easy}\n付きにくい: {hard}".format(text=gear_power, easy=easy_brand_names, hard=hard_brand_names))
            ]
        )

    elif re.fullmatch(r'ブランド', text):
        # ブランド名一覧を取得
        cur.execute('select brand_name from brand')
        res = cur.fetchall()
        brand_name = [flatten for inner in res for flatten in inner]
        brand_name = "\n".join(brand_name)

        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(
                    text="{brand_name}".format(brand_name=brand_name))
            ]
        )
    
    elif re.fullmatch(r'サブ', text):
        line_bot_api.reply_message(
            event.reply_token, 
            TextSendMessage(text='一覧から選んでね',
                    quick_reply=QuickReply(items=[
                        QuickReplyButton(action=MessageAction(label="スプラッシュボム", text="スプラッシュボム")),
                        QuickReplyButton(action=MessageAction(label="ポイントセンサー", text="ポイントセンサー")),
                        QuickReplyButton(action=MessageAction(label="ポイズンミスト", text="ポイズンミスト")),
                        QuickReplyButton(action=MessageAction(label="キューバンボム", text="キューバンボム")),
                        QuickReplyButton(action=MessageAction(label="カーリングボム", text="カーリングボム")),
                        QuickReplyButton(action=MessageAction(label="スプリンクラー", text="スプリンクラー")),
                        QuickReplyButton(action=MessageAction(label="クイックボム", text="クイックボム")),
                        QuickReplyButton(action=MessageAction(label="ロボットボム", text="ロボットボム")),
                        QuickReplyButton(action=MessageAction(label="ジャンプビーコン", text="ジャンプビーコン")),
                        QuickReplyButton(action=MessageAction(label="スプラッシュシールド", text="スプラッシュシールド")),
                        QuickReplyButton(action=MessageAction(label="トラップ", text="トラップ")),
                        QuickReplyButton(action=MessageAction(label="タンサンボム", text="タンサンボム")),
                        QuickReplyButton(action=MessageAction(label="トーピード", text="トーピード")),
                    ])
            )
        )



    elif m_time_range:
        battle_stage.get_stage_time_range(line_bot_api, event, m_time_range)


if __name__ == "__main__":
    app.run()
