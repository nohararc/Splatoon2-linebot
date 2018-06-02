# -*- coding: utf-8 -*-

import os
import unittest
from unittest.mock import MagicMock
from linebot import (
    LineBotApi, SignatureValidator, WebhookParser, WebhookHandler
)

from linebot.models import (
    TextSendMessage
)

import app

class TestSalmon(unittest.TestCase):

    file_dir = os.path.dirname(__file__)
    salmon_json_path = os.path.join(file_dir, 'salmon.json')
    with open(salmon_json_path, encoding="utf-8") as fp:
        body = fp.read()

    # mock
    parser = WebhookParser('channel_secret')
    parser.signature_validator.validate = lambda a, b: True
    events = parser.parse(body, 'channel_secret')

    def setUp(self):
        app.line_bot_api.reply_message = MagicMock()

    def test_salmon(self):
        app.handle_message(self.events[0])
        _, textsendmessage = app.line_bot_api.reply_message.call_args[0]
        self.assertRegex(textsendmessage[0].text, r'(オープン！|クローズ！)\n(\d{2}/\d{2} \d{2}:\d{2}) ～ (\d{2}/\d{2} \d{2}:\d{2})\n(.+)')

        app.handle_message(self.events[1])
        _, textsendmessage = app.line_bot_api.reply_message.call_args[0]
        self.assertRegex(textsendmessage[0].text, r'(オープン！|クローズ！)\n(\d{2}/\d{2} \d{2}:\d{2}) ～ (\d{2}/\d{2} \d{2}:\d{2})\n(.+)')

class TestRandom(unittest.TestCase):

    file_dir = os.path.dirname(__file__)
    random_json_path = os.path.join(file_dir, 'random.json')
    with open(random_json_path, encoding="utf-8") as fp:
        body = fp.read()

    # mock
    parser = WebhookParser('channel_secret')
    parser.signature_validator.validate = lambda a, b: True
    events = parser.parse(body, 'channel_secret')

    def setUp(self):
        app.line_bot_api.reply_message = MagicMock()

    def test_random_rule(self):
        app.handle_message(self.events[0])
        _, textsendmessage = app.line_bot_api.reply_message.call_args[0]
        self.assertRegex(textsendmessage[0].text, r"(ナワバリ)|(ガチ)(ヤグラ|ホコバトル|エリア|アサリ)")

    def test_random_weapon(self):
        app.handle_message(self.events[1])
        _, textsendmessage = app.line_bot_api.reply_message.call_args[0]
        self.assertRegex(textsendmessage[0].text, r"ブキ: .+\nサブ: .+\nスペシャル: .+")

class TestStage(unittest.TestCase):

    file_dir = os.path.dirname(__file__)
    stage_json_path = os.path.join(file_dir, 'stage.json')
    with open(stage_json_path, encoding="utf-8") as fp:
        body = fp.read()

    # mock
    parser = WebhookParser('channel_secret')
    parser.signature_validator.validate = lambda a, b: True
    events = parser.parse(body, 'channel_secret')

    def setUp(self):
        app.line_bot_api.reply_message = MagicMock()

    def test_stage(self):
        app.handle_message(self.events[0])
        _, textsendmessage = app.line_bot_api.reply_message.call_args[0]
        self.assertRegex(textsendmessage[0].text, r"(\d{2}/\d{2} \d{2}:\d{2}) ～ (\d{2}/\d{2} \d{2}:\d{2})\n(ガチ)(ヤグラ|ホコバトル|エリア|アサリ)\n.+\n.+")

        app.handle_message(self.events[1])
        _, textsendmessage = app.line_bot_api.reply_message.call_args[0]
        self.assertRegex(textsendmessage[0].text, r"(\d{2}/\d{2} \d{2}:\d{2}) ～ (\d{2}/\d{2} \d{2}:\d{2})\n(ガチ)(ヤグラ|ホコバトル|エリア|アサリ)\n.+\n.+")

        app.handle_message(self.events[2])
        _, textsendmessage = app.line_bot_api.reply_message.call_args[0]
        self.assertRegex(textsendmessage[0].text, r"(\d{2}/\d{2} \d{2}:\d{2}) ～ (\d{2}/\d{2} \d{2}:\d{2})\nナワバリバトル\n.+\n.+")

    def test_stage_time_oddnum(self):
        app.handle_message(self.events[3])
        _, textsendmessage = app.line_bot_api.reply_message.call_args[0]
        self.assertRegex(textsendmessage[0].text, r"(\d{2}/\d{2} \d{2}:\d{2}) ～ (\d{2}/\d{2} \d{2}:\d{2})\n(ガチ)(ヤグラ|ホコバトル|エリア|アサリ)\n.+\n.+")

        app.handle_message(self.events[4])
        _, textsendmessage = app.line_bot_api.reply_message.call_args[0]
        self.assertRegex(textsendmessage[0].text, r"(\d{2}/\d{2} \d{2}:\d{2}) ～ (\d{2}/\d{2} \d{2}:\d{2})\n(ガチ)(ヤグラ|ホコバトル|エリア|アサリ)\n.+\n.+")

        app.handle_message(self.events[5])
        _, textsendmessage = app.line_bot_api.reply_message.call_args[0]
        self.assertRegex(textsendmessage[0].text, r"(\d{2}/\d{2} \d{2}:\d{2}) ～ (\d{2}/\d{2} \d{2}:\d{2})\nナワバリバトル\n.+\n.+")

class TestWeapon(unittest.TestCase):

    file_dir = os.path.dirname(__file__)
    weapon_json_path = os.path.join(file_dir, 'weapon.json')
    with open(weapon_json_path, encoding="utf-8") as fp:
        body = fp.read()

    # mock
    parser = WebhookParser('channel_secret')
    parser.signature_validator.validate = lambda a, b: True
    events = parser.parse(body, 'channel_secret')

    def setUp(self):
        app.line_bot_api.reply_message = MagicMock()

    def test_weapon(self):
        app.handle_message(self.events[0])
        _, textsendmessage = app.line_bot_api.reply_message.call_args[0]
        self.assertRegex(textsendmessage[0].text, r"ブキ: スプラシューターコラボ\nサブ: スプラッシュボム\nスペシャル: ジェットパック")


class TestBrand(unittest.TestCase):

    file_dir = os.path.dirname(__file__)
    weapon_json_path = os.path.join(file_dir, 'brand.json')
    with open(weapon_json_path, encoding="utf-8") as fp:
        body = fp.read()

    # mock
    parser = WebhookParser('channel_secret')
    parser.signature_validator.validate = lambda a, b: True
    events = parser.parse(body, 'channel_secret')

    def setUp(self):
        app.line_bot_api.reply_message = MagicMock()

    def test_brand_to_gear(self):
        app.handle_message(self.events[0])
        _, textsendmessage = app.line_bot_api.reply_message.call_args[0]
        self.assertRegex(textsendmessage[0].text, r"ブランド: .+\n付きやすい: .+\n付きにくい: .+")

    def test_gear_to_brand(self):
        app.handle_message(self.events[1])
        _, textsendmessage = app.line_bot_api.reply_message.call_args[0]
        self.assertRegex(textsendmessage[0].text, r"ギア: .+\n付きやすい: .+\n付きにくい: .+")


if __name__ == '__main__':
    unittest.main()
