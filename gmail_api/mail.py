from typing import Optional

from .gmail_process import MessageHandler, gmail


class Mail:
    def __init__(
        self,
        message_id: str,
        mail_id: str,
        summary: Optional[str] = None,
        label: Optional[str] = None,
    ):
        """
        Args:
            id (str): 메일 ID
        """
        message = gmail.get_message_details(message_id)
        body, attachments = MessageHandler.process_message(message)
        headers = MessageHandler.process_headers(message)

        self._id = mail_id
        self.sender = headers["sender"]
        self.recipients = [headers["recipients"]]
        self.subject = headers["subject"]
        self.body = body
        self.cc = [headers["cc"]] if headers["cc"] is not None else []
        self.attachments = attachments if attachments is not None else []
        self.date = headers["date"]
        self._summary = summary
        self._label = label
        self._similar_mails = []

    def __str__(self) -> str:
        """
        사람이 읽기 좋은 형태로 Mail 객체를 출력하도록 합니다.
        """
        attachments_text = ""
        if self.attachments:
            for i, item in enumerate(self.attachments):
                attachments_text += "첨부파일 " + str(i + 1) + ":\n" + item + "\n\n"
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
    def label(self) -> Optional[str]:
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        if not value:
            raise ValueError("Label cannot be empty.")
        self._label = value

    @property
    def similar_mails(self) -> Optional[list[str]]:
        return self._similar_mails

    @similar_mails.setter
    def similar_mails(self, value: list[str]) -> None:
        if not isinstance(value, list) and not value:
            raise ValueError("Similar Mails cannot be empty.")
        self._similar_mails = value
