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

def get_subspe(line_bot_api, event, text, sub, special):
    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text="ブキ: {weapon}\nサブ: {sub}\nスペシャル: {special}".format(
                weapon=text,
                sub=sub,
                special=special
            ))
        ]
    )