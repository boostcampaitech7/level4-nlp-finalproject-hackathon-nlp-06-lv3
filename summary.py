import os

import dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_upstage import ChatUpstage


def summary(mails, debug=False):
    chat = ChatUpstage(api_key=os.getenv("UPSTAGE_API_KEY"), model="solar-pro")

    summarized_mails = []
    for mail in mails:
        messages = [
            SystemMessage(
                content="당신은 사용자의 메일을 대신 읽고 주요한 내용을 정리해주는 AI Assistant입니다. 주어지는 메일에 대해 한국어로 간략하게 요약을 해주세요."
            ),
            HumanMessage(content=mail),
        ]
        response = chat.invoke(messages)
        if debug:
            print(response.content)
        summarized_mails.append(response.content)

    messages = [
        SystemMessage(
            content="당신은 사용자의 메일을 대신 읽고 주요한 내용을 정리해주는 AI Assistant입니다. 다음의 요약된 메일들을 보고 일일보고를 만들어주세요. "
            "사용자에게 중요할 내용을 위주로 알려주세요.\n"
            "다음과 같은 분류로 메일을 분류하여 각 분류에서 사용자가 알아야하는 내용을 정리해주어야합니다.\n"
            "분류: 답장을 해야하는 메일/할일 목록에 넣어야하는 메일/기타"
        ),
        HumanMessage(content="\n".join(summarized_mails)),
    ]
    response = chat.invoke(messages)
    return response.content


if __name__ == "__main__":
    dotenv.load_dotenv()
    with (
        open("samples/mail1.txt", "r", encoding="utf-8") as file1,
        open("samples/mail2.txt", "r", encoding="utf-8") as file2,
    ):
        sample_mails = [file1.read(), file2.read()]

    result = summary(sample_mails, debug=True)
    print("=" * 30)
    print("Summary")
    print("=" * 30)
    print(result)
