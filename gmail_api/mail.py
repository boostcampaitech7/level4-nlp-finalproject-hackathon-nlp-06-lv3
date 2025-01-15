from datetime import datetime
from typing import List, Optional


class Mail:
    def __init__(
        self,
        sender: str,
        recipients: List[str],
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        # attachments: Optional[List[str]] = None,
        date: Optional[str] = None,
    ):
        """
        :param sender: 이메일을 보낸 사람의 주소
        :param recipients: 이메일을 받는 사람(들)의 주소 목록
        :param subject: 이메일 제목
        :param body: 이메일 본문(텍스트 형태)
        :param cc: 참조할 사람(들)의 주소 목록
        # 일단 제외:param attachments: 첨부 파일 경로나 파일 이름 등의 목록
        :param date: 이메일 수신 시간간
        """
        self.sender = sender
        self.recipients = recipients
        self.subject = subject
        self.body = body
        self.cc = cc if cc is not None else []
        # self.attachments = attachments if attachments is not None else []
        self.date = date

    def __str__(self) -> str:
        """
        사람이 읽기 좋은 형태로 Mail 객체를 출력하도록 합니다.
        """
        return (
            f"From: {self.sender}\n"
            f"To: {', '.join(self.recipients)}\n"
            f"CC: {', '.join(self.cc)}\n"
            f"Subject: {self.subject}\n"
            f"Date: {self.date}\n"
            f"Body:\n{self.body}\n"
            # f"Attachments: {', '.join(self.attachments)}"
        )


if __name__ == "__main__":
    sender = "canolayoo78@gmail.com"
    recipients = ["yce9110@gmail.com"]
    subject = "[모둠초밥] 새해 인사 드립니다."
    body = "2025년 을사년 푸른 뱀의 해가 밝았습니다."
    cc = ["chamjo@gmail.com"]
    # attachments: Optional[List[str]] = None,
    date = datetime.now()

    mail = Mail(sender, recipients, subject, body, cc, date)
    print(mail)
