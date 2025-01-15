import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_upstage import ChatUpstage


def total_report(classified_mail, debug=False):
    chat = ChatUpstage(api_key=os.getenv("UPSTAGE_API_KEY"), model="solar-pro")
    with open("prompt/report.txt", "r", encoding="utf-8") as file:
        content = file.read()
    messages = [
        SystemMessage(content=content),
        HumanMessage(content="\n".join(classified_mail)),
    ]
    response = chat.invoke(messages)
    return response.content
