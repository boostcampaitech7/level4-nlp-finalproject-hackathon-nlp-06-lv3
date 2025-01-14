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
            content="당신은 사용자의 메일을 대신 읽고 주요한 내용을 정리해주는 AI Assistant입니다. 다음의 요약된 메일들을 보고 일일보고를 만들어주세요. 사용자에게 중요할 내용을 위주로 알려주세요.\n"
            "다음과 같은 분류로 메일을 분류하여 각 분류에서 사용자가 알아야하는 내용을 정리해주어야합니다.\n"
            "분류: 답장을 해야하는 메일/할일 목록에 넣어야하는 메일/기타"
        ),
        HumanMessage(content="\n".join(summarized_mails)),
    ]
    response = chat.invoke(messages)
    return response.content


if __name__ == "__main__":
    dotenv.load_dotenv()

    sample_mails = [
        """AWS Budgets: My Zero-Spend Budget has exceeded your alert threshold
budgets@costalerts.amazonaws.com
1월 4일 (토) 오전 3:41 (9일 전)

Description: awslogo



Dear AWS Customer,

You requested that we alert you when the actual cost associated with your My Zero-Spend Budget budget exceeds $0.01 for the current month. The month actual cost associated with this budget is $0.60. You can find additional details below and by accessing the AWS Budgets dashboard.

Budget Name	Budget Type	Budgeted Amount	Alert Type	Alert Threshold	ACTUAL Amount
My Zero-Spend Budget	Cost	$1.00	ACTUAL	> $0.01	$0.60

Go to the AWS Budgets dashboard







If you wish to stop receiving notifications, please click here to request opting out of this notification. Please do not reply directly to this email. If you have any questions or comments regarding this email, please contact us at https://aws.amazon.com/support

This message was produced and distributed by Amazon Web Services, Inc., 410 Terry Avenue North, Seattle, Washington 98109-5210. AWS will not be bound by, and specifically objects to, any term, condition or other provision which is different from or in addition to the provisions of the AWS Customer Agreement or AWS Enterprise Agreement between AWS and you (whether or not it would materially alter such AWS Customer Agreement or AWS Enterprise Agreement) and which is submitted in any order, receipt, acceptance, confirmation, correspondence or otherwise, unless AWS specifically agrees to such provision in a written instrument signed by AWS.""",
        """Re: [yoshi389111/github-profile-3d-contrib] Deprecation Warning for Node.js 16 in GitHub Actions: Update Required (Issue #77)
받은편지함

Louis-Guillaume MORAND <notifications@github.com> 수신거부
1월 1일 (수) 오후 7:28 (12일 전)
yoshi389111/github-profile-3d-contrib, 나, Author에게

I did my own version with some PR included: https://github.com/lgmorand/github-profile-3d-contrib

—
Reply to this email directly, view it on GitHub, or unsubscribe.
You are receiving this because you authored the thread.

""",
    ]
    result = summary(sample_mails, debug=True)
    print("=" * 30)
    print("Summary")
    print("=" * 30)
    print(result)
