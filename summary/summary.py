import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_upstage import ChatUpstage

from gmail_api import Mail


def summarize(chat: ChatUpstage, mail: list[Mail] | Mail, prompt: str):
    cur_dir = os.path.dirname(__file__)
    project_dir = os.path.dirname(cur_dir)
    prompt_path = os.path.join(project_dir, "prompt", f"{prompt}.txt")
    with open(prompt_path, "r", encoding="utf-8") as file:
        content = file.read()

    concated_mails = ""
    if isinstance(mail, list):
        concated_mails = "\n".join((mail))
    else:
        concated_mails = str(mail)

    messages = [
        SystemMessage(content=content),
        HumanMessage(content=concated_mails),
    ]
    response = chat.invoke(messages)
    return response.content
