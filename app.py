from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('dI1mDsEwhTMV8F4SadBPlSyxtW+OQiWeK3XYzty/sGx1gn0Ihx81PmtGa6wugH/17M3xgom+0Dy/708CEkUb0ohhgXqxJE1kbRP1K5kjig+1aEwDfxhh9ZvbhFF9IX3X7fUlXYEPePEzQmk3BH1CxwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('b700b14f01a738fea4fc22c8f29c175d')

@app.route("/")
def hello_world():
    return "hello world!"

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
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    app.run()
