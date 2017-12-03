# -*- encoding: utf-8 -*-

import urllib
import json
from datetime import datetime
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, ImagemapSendMessage
)


def get_subspe(line_bot_api, event, name, sub, special):
    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text="ブキ: {weapon}\nサブ: {sub}\nスペシャル: {special}".format(
                weapon=name,
                sub=sub,
                special=special
            ))
        ]
    )


def get_weapons(line_bot_api, event, text, *names):
    weapons = []
    weapons = "\n".join(names)
    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text="{text}のブキ一覧\n{weapons}".format(
                text=text,
                weapons=weapons
            ))
        ]
    )
