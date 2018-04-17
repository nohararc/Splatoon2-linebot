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
    def test_salmon(self):
        file_dir = os.path.dirname(__file__)
        webhook_sample_json_path = os.path.join(file_dir, 'webhook.json')
        with open(webhook_sample_json_path, encoding="utf-8") as fp:
            body = fp.read()

        parser = WebhookParser('channel_secret')
        # mock
        parser.signature_validator.validate = lambda a, b: True

        events = parser.parse(body, 'channel_secret')
        app.line_bot_api.reply_message = MagicMock()
        app.handle_message(events[0])

        res = app.line_bot_api.reply_message.call_args
        _, textsendmessage = res[0]
        self.assertRegex(textsendmessage[0].text, r'(\d{2}/\d{2} \d{2}:\d{2}) ～ (\d{2}/\d{2} \d{2}:\d{2})\n(.+)')

class TestRandomRule(unittest.TestCase):
    def test_random_rule(self):
        file_dir = os.path.dirname(__file__)
        webhook_sample_json_path = os.path.join(file_dir, 'webhook.json')
        with open(webhook_sample_json_path, encoding="utf-8") as fp:
            body = fp.read()

        parser = WebhookParser('channel_secret')
        # mock
        parser.signature_validator.validate = lambda a, b: True

        events = parser.parse(body, 'channel_secret')
        app.line_bot_api.reply_message = MagicMock()
        app.handle_message(events[1])

        res = app.line_bot_api.reply_message.call_args
        _, textsendmessage = res[0]
        self.assertRegex(textsendmessage[0].text, r"(ナワバリ)|(ガチ)(ヤグラ|ホコ|エリア|アサリ)")



if __name__ == '__main__':
    unittest.main()
