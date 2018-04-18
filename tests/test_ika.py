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
    webhook_sample_json_path = os.path.join(file_dir, 'webhook.json')
    with open(webhook_sample_json_path, encoding="utf-8") as fp:
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
        self.assertRegex(textsendmessage[0].text, r'(\d{2}/\d{2} \d{2}:\d{2}) ～ (\d{2}/\d{2} \d{2}:\d{2})\n(.+)')

class TestRandom(unittest.TestCase):

    file_dir = os.path.dirname(__file__)
    webhook_sample_json_path = os.path.join(file_dir, 'webhook.json')
    with open(webhook_sample_json_path, encoding="utf-8") as fp:
        body = fp.read()

    # mock
    parser = WebhookParser('channel_secret')
    parser.signature_validator.validate = lambda a, b: True
    events = parser.parse(body, 'channel_secret')

    def setUp(self):
        app.line_bot_api.reply_message = MagicMock()

    def test_random_rule(self):
        app.handle_message(self.events[1])
        _, textsendmessage = app.line_bot_api.reply_message.call_args[0]
        self.assertRegex(textsendmessage[0].text, r"(ナワバリ)|(ガチ)(ヤグラ|ホコ|エリア|アサリ)")

    def test_random_weapon(self):
        app.handle_message(self.events[2])
        res = app.line_bot_api.reply_message.call_args
        _, textsendmessage = res[0]
        self.assertRegex(textsendmessage[0].text, r"ブキ: .+\nサブ: .+\nスペシャル: .+")


if __name__ == '__main__':
    unittest.main()
