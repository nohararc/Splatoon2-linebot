import urllib
import json
from datetime import datetime
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, ImagemapSendMessage
)

def get_battle_stage(line_bot_api, event, rule):
    req = urllib.request.Request(
        "https://spla2.yuu26.com/{rule}/now".format(rule=rule))
    req.add_header("user-agent", "@nohararc")
    with urllib.request.urlopen(req) as res:
        response_body = res.read().decode("utf-8")
        response_json = json.loads(response_body.split("\n")[0])
        data = response_json["result"][0]

        now_start = datetime.strptime(data["start"], '%Y-%m-%dT%H:%M:%S')
        now_end = datetime.strptime(data["end"], '%Y-%m-%dT%H:%M:%S')

        line_bot_api.reply_message(
            event.reply_token, [
                TextSendMessage(text="{start} ～ {end}\n{rule}\n{stage1}\n{stage2}".format(
                    start=now_start.strftime("%m/%d %H:%M"), end=now_end.strftime("%m/%d %H:%M"),
                    rule=data["rule_ex"]["name"],
                    stage1=data["maps_ex"][0]["name"], stage2=data["maps_ex"][1]["name"]
                ))
            ]
        )

def get_specified_battle_stage(line_bot_api, event, rule, m):
    req = urllib.request.Request(
        "https://spla2.yuu26.com/{rule}/schedule".format(rule=rule))
    req.add_header("user-agent", "@nohararc")
    with urllib.request.urlopen(req) as res:
        response_body = res.read().decode("utf-8")
        response_json = json.loads(response_body.split("\n")[0])
        data = response_json["result"]
        for d in data:
            start_time = datetime.strptime(d["start"], '%Y-%m-%dT%H:%M:%S')
            end_time = datetime.strptime(d["end"], '%Y-%m-%dT%H:%M:%S')
            start_hour = start_time.strftime("%H")
            if int(m.group(1)) == int(start_hour):
                line_bot_api.reply_message(
                    event.reply_token, [
                        TextSendMessage(text="{start} ～ {end}\n{rule}\n{stage1}\n{stage2}".format(
                            start=start_time.strftime("%m/%d %H:%M"),
                            end=end_time.strftime("%m/%d %H:%M"),
                            rule=d["rule_ex"]["name"],
                            stage1=d["maps_ex"][0]["name"], stage2=d["maps_ex"][1]["name"]
                        ))
                    ]
                )