from typing import List, Optional


class Mail:
    def __init__(
        self,
        id: str,
        sender: str,
        recipients: List[str],
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        attachments: Optional[List[str]] = None,
        date: Optional[str] = None,
        summary: Optional[str] = None,
        label: Optional[str] = None,
    ):
        """
        Args:
            id (str): 메일 ID
            sender (str): 이메일을 보낸 사람의 주소
            recipients (List[str]): 이메일을 받는 사람(들)의 주소 목록
            subject (str): 이메일 제목
            body (str): 이메일 본문(텍스트 형태)
            cc (Optional[List[str]], optional): 참조할 사람(들)의 주소 목록. 기본 값은 None
            attachments (Optional[List[str]], optional): 첨부 파일 경로나 파일 이름 등의 목록. 기본 값은 None.
            date (Optional[str], optional): 이메일 수신 시간. 기본 값은 None.
            summary (Optional[str], optional): 이메일 요약문. 기본 값은 None.
            label (Optional[str], optional): 분류된 메일 종류. 기본 값은 None.
        """
        self._id = id
        self.sender = sender
        self.recipients = recipients
        self.subject = subject
        self.body = body
        self.cc = cc if cc is not None else []
        self.attachments = attachments if attachments is not None else []
        self.date = date
        self._summary = summary
        self._label = label

    def __str__(self) -> str:
        """
        사람이 읽기 좋은 형태로 Mail 객체를 출력하도록 합니다.
        """
        attachments_text = ""
        if self.attachments:
            for i, item in enumerate(self.attachments):
                attachments_text += "Attachments " + str(i + 1) + ":\n" + item + "\n\n"
        return (
            f"From: {self.sender}\n"
            f"To: {', '.join(self.recipients)}\n"
            f"CC: {', '.join(self.cc)}\n"
            f"Subject: {self.subject}\n"
            f"Date: {self.date}\n"
            f"Body:\n{self.body}\n"
            f"{attachments_text}"
        )

    @property
    def id(self) -> str:
        return self._id

    @property
    def summary(self) -> Optional[str]:
        return self._summary

    @summary.setter
    def summary(self, value: str) -> None:
        if not value:
            raise ValueError("Summary cannot be empty.")
        self._summary = value

    @property
    def label(self) -> Optional[str]:
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        if not value:
            raise ValueError("Label cannot be empty.")
        self._label = value
