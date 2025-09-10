import os
import smtplib

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from typing import Type

class newsletter_input(BaseModel):
    """Input schema for the NewsletterEmailer tool."""
    body: str = Field(..., description="HTML content of the newsletter email.")

class send_newsletter(BaseTool):
    name: str = "Newsletter Emailer"
    description: str = "Sends a generated newsletter via email to multiple recipients."
    args_schema: Type[BaseModel] = newsletter_input

    def _run(self, body: str) -> str:
        """Send the generated newsletter via email to multiple recipients."""
        try:
            msg = MIMEMultipart()
            from_email = os.getenv("FROM_EMAIL")
            to_emails = os.getenv("TO_EMAIL")

            if not from_email:
                return "Error: FROM_EMAIL environment variable is not set."

            if not to_emails:
                return "Error: TO_EMAIL environment variable is not set."

            to_email_list = to_emails.split(',')
            msg['From'] = from_email
            msg['To'] = ', '.join(to_email_list)
            msg['Subject'] = "GenAI Newsletter"

            # Attach the HTML body
            msg.attach(MIMEText(body, 'html', 'utf-8'))

            # Attach the image
            image_path = 'image.png'
            if os.path.exists(image_path):
                with open(image_path, 'rb') as fp:
                    image = MIMEImage(fp.read())
                image.add_header('Content-ID', '<banner>')
                msg.attach(image)
            else:
                return f"Error: Image file '{image_path}' not found."

            # Send the email
            with smtplib.SMTP('smtp.gmail.com', 587, timeout=60) as server:
                server.starttls()
                email_password = os.getenv("EMAIL_PASSWORD")
                if not email_password:
                    return "Error: EMAIL_PASSWORD environment variable is not set."
                server.login(from_email, email_password)
                server.send_message(msg)

            return f"Email successfully sent to {len(to_email_list)} recipients!"

        except smtplib.SMTPException as e:
            return f"SMTP error occurred while sending the email: {str(e)}"
        except Exception as e:
            return f"An error occurred while sending the email: {str(e)}"