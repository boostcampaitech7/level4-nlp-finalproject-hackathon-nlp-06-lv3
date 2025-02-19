class Mail:
    def __init__(
        self,
        message_id: str,
        mail_id: str,
        body: str,
        attachments: list[str],
        headers: dict[str, str],
    ):
        """
        Args:
            gmail_service: GmailService (이미 인증된 Gmail API 서비스 객체 래퍼)
            message_id (str): Gmail 상에서의 message id
            mail_id (str): 우리 서비스 내에서 매길 임의 id
        """
        self.message_id = message_id
        self.id = mail_id
        self.sender = headers["sender"]
        self.recipients = [headers["recipients"]]
        self.subject = headers["subject"]
        self.body = body
        self.cc = [headers["cc"]] if headers["cc"] is not None else []
        self.attachments = attachments if attachments is not None else []
        self.date = headers["date"]

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
