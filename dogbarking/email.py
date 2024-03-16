from pathlib import Path
import textwrap
from pydantic import BaseModel, EmailStr, SecretStr
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from loguru import logger


class Email(BaseModel):
    sender_email: EmailStr
    receiver_email: EmailStr
    attachment_filepath: Path
    smtp_password: SecretStr
    smtp_server: str
    smtp_port: int = 465

    class Config:
        arbitrary_types_allowed = True

    def _create_message(self) -> MIMEMultipart:
        """Create the email message with attachment."""
        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = self.receiver_email
        message["Subject"] = f"Dog Barking Alert {datetime.now().isoformat()}"
        body = textwrap.dedent(
            f"""\
        Your dog was barking at {datetime.now().isoformat()}.
        """
        )

        # Add body to email
        message.attach(MIMEText(body, "plain"))

        # Open PDF file in binary mode and attach
        with self.attachment_filepath.open("rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {str(self.attachment_filepath)}",
        )
        message.attach(part)

        return message

    def send_email(self) -> None:
        """Send the email using the details provided."""
        logger.info(f"Sending email to {self.receiver_email}...")
        message = self._create_message()
        text = message.as_string()

        # Log in to server using secure context and send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
            self.smtp_server, self.smtp_port, context=context
        ) as server:
            server.ehlo()
            if self.smtp_port != 465:
                server.starttls(context=context)  # Secure the connection
                server.ehlo()
            server.login(self.sender_email, self.smtp_password.get_secret_value())
            server.sendmail(self.sender_email, self.receiver_email, text)
