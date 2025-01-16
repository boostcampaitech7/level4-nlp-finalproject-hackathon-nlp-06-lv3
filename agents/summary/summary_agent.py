import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_upstage import ChatUpstage

from gmail_api import Mail
from prompt import load_template


class SummaryAgent:
    def __init__(self, summary_type: str, temperature=None, seed=None):
        load_dotenv()
        self.chat = ChatUpstage(
            api_key=os.getenv("UPSTAGE_API_KEY"), model="solar-pro", temperature=temperature, seed=seed
        )
        self.summary_type = summary_type

    def summarize(self, mail: list | Mail):
        template = load_template("summary", f"{self.summary_type}.txt")
        concated_mails = ""
        if isinstance(mail, list):
            concated_mails = "\n".join((mail))
        else:
            concated_mails = str(mail)

        messages = [
            SystemMessage(content=template),
            HumanMessage(content=concated_mails),
        ]
        response = self.chat.invoke(messages)
        return response.content
