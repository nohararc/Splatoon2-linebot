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


def command_list(line_bot_api, event):
    line_bot_api.reply_message(
        event.reply_token, [
            TextSendMessage(text="{league}\n{gachi}\n{regular}\n{salmon}\n{buki}".format(
                league="(リーグマッチ|リグマ)(\d+)?(時)?",
                gachi="(ガチマッチ|ガチマ)(\d+)?(時)?",
                regular="(レギュラーマッチ|ナワバリ)(\d+)?(時)?",
                salmon="サーモンラン",
                buki="{ブキ名}"
            ))
        ]
    )
