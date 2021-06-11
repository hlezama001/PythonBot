from flask import Flask,request,Response,render_template
from botbuilder.core import BotFrameworkAdapter,BotFrameworkAdapterSettings,TurnContext,ConversationState,MemoryStorage
from botbuilder.schema import Activity
import asyncio
from botdialog import BotDialog

app = Flask(__name__)
loop = asyncio.get_event_loop()

botsettings = BotFrameworkAdapterSettings("f75254ef-a036-46d3-971f-30e139dcf19b","Zr4o3g0r-IcE6Lc_xPv-5huU4-1ZpNDXaT")
botadapter = BotFrameworkAdapter(botsettings)

CONMEMORY = ConversationState(MemoryStorage())
botdialog = BotDialog(CONMEMORY)


@app.route("/api/messages",methods=["POST"])
def messages():
    if "application/json" in request.headers["content-type"]:
        body = request.json
    else:
        return Response(status = 415)

    activity = Activity().deserialize(body)

    auth_header = (request.headers["Authorization"] if "Authorization" in request.headers else "")

    async def call_fun(turncontext):
        await botdialog.on_turn(turncontext)

    task = loop.create_task(
        botadapter.process_activity(activity,auth_header,call_fun)
        )
    loop.run_until_complete(task)

@app.route('/', methods = ['GET', 'POST'])
def web():
    return render_template('bot.html')

if __name__ == '__main__':
    app.run('localhost',3978)
