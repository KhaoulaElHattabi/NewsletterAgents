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
            msg['From'] = os.getenv("FROM_EMAIL")

            # Récupérer et traiter la chaîne des destinataires
            to_emails = os.getenv("TO_EMAIL", "").replace('"', '').split(',')
            to_emails = [email.strip() for email in to_emails if email.strip()]

            if not to_emails:
                return "Erreur : Aucun destinataire valide spécifié dans TO_EMAIL"

            msg['To'] = ', '.join(to_emails)
            msg['Subject'] = "GenAI Newsletter"

            # Encode the body as UTF-8
            msg.attach(MIMEText(body.encode('utf-8'), 'html', 'utf-8'))

            # Add the image
            with open('image.png', 'rb') as fp:
                image = MIMEImage(fp.read())
            image.add_header('Content-ID', '<Mailtrapimage>')
            msg.attach(image)

            with smtplib.SMTP('smtp.gmail.com', 587, timeout=60) as server:
                server.starttls()
                server.login(os.getenv("FROM_EMAIL"), os.getenv("EMAIL_PASSWORD"))
                server.send_message(msg)
            return f"Email envoyé avec succès à {len(to_emails)} destinataires!"
        except smtplib.SMTPException as e:
            return f"Erreur SMTP lors de l'envoi de l'email: {str(e)}"
        except Exception as e:
            return f"Erreur lors de l'envoi de l'email: {str(e)}"