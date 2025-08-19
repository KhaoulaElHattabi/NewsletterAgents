from email.mime.image import MIMEImage
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import smtplib
from langchain.tools import tool



@tool("Newsletter Emailer")
def send_newsletter(body: str) -> str:
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
        msg['Subject'] = Header("GenAI Newsletter", 'utf-8')

        # Encode the body as UTF-8
        msg.attach(MIMEText(body.encode('utf-8'), 'html', 'utf-8'))
        
        # Add the image
        with open('banner.jpg', 'rb') as fp:
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
    
    