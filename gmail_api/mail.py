from typing import Optional


class Mail:
    def __init__(
        self,
        message_id: str,
        mail_id: str,
        body: str,
        attachments: list[str],
        headers: dict[str, str],
        summary: Optional[str] = None,
        label: Optional[str] = None,
    ):
        """
        Args:
            gmail_service: GmailService (이미 인증된 Gmail API 서비스 객체 래퍼)
            message_id (str): Gmail 상에서의 message id
            mail_id (str): 우리 서비스 내에서 매길 임의 id
        """
        self.message_id = message_id
        self._id = mail_id
        self.sender = headers["sender"]
        self.recipients = [headers["recipients"]]
        self.subject = headers["subject"]
        self.body = body
        self.cc = [headers["cc"]] if headers["cc"] is not None else []
        self.attachments = attachments if attachments is not None else []
        self.date = headers["date"]
        self._summary = summary
        self._label_category = label
        self._label_action = label
        self._similar_mails = []

    def __str__(self) -> str:
        attachments_text = ""
        if self.attachments:
            for i, item in enumerate(self.attachments):
                attachments_text += f"첨부파일 {i + 1}:\n{item}\n\n"
        return (
            f"보낸 사람: {self.sender}\n"
            f"받는 사람: {', '.join(self.recipients)}\n"
            f"참조: {', '.join(self.cc)}\n"
            f"제목: {self.subject}\n"
            f"날짜: {self.date}\n"
            f"본문:\n{self.body}\n"
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
    def label_category(self) -> Optional[str]:
        return self._label_category

    @label_category.setter
    def label_category(self, value: str) -> None:
        if not value:
            raise ValueError("Label cannot be empty.")
        self._label_category = value

    @property
    def label_action(self) -> Optional[str]:
        return self._label_action

    @label_action.setter
    def label_action(self, value: str) -> None:
        if not value:
            raise ValueError("Label cannot be empty.")
        self._label_action = value

    @property
    def similar_mails(self) -> Optional[list[str]]:
        return self._similar_mails

    @similar_mails.setter
    def similar_mails(self, value: list[str]) -> None:
        if not isinstance(value, list) and not value:
            raise ValueError("Similar Mails cannot be empty.")
        self._similar_mails = value
