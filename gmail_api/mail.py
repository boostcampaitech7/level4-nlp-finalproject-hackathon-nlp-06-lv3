from typing import Optional

from gmail_api import GmailService, MessageHandler


class Mail:
    def __init__(
        self,
        message_id: str,
        mail_id: str,
        gmail_service: GmailService,
        summary: Optional[str] = None,
        label: Optional[str] = None,
    ):
        """
        Args:
            id (str): 메일 ID
            gmail_service: GmailService 객체
        """
        message = gmail_service.get_message_details(message_id)
        body, attachments = MessageHandler.process_message(gmail_service.service, message)
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
