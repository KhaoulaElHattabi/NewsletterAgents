import os
from langchain.tools import tool
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import smtplib
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper

numbers_of_articles = 5
api_key=os.getenv("TAVILY_API_KEY")
tavily_wrapper = TavilySearchAPIWrapper(tavily_api_key=api_key)


@tool("Tavily Search")
def tavily_search():
    """Search for the latest AI developments using Tavily."""
tavily_tool = TavilySearchResults(
    max_results=numbers_of_articles,
    exclude_domains=["wikipedia.org"],
    api_wrapper=tavily_wrapper
)


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
        
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=60) as server:
            server.starttls()
            server.login(os.getenv("FROM_EMAIL"), os.getenv("EMAIL_PASSWORD"))
            server.send_message(msg)
        return f"Email envoyé avec succès à {len(to_emails)} destinataires!"
    except smtplib.SMTPException as e:
        return f"Erreur SMTP lors de l'envoi de l'email: {str(e)}"
    except Exception as e:
        return f"Erreur lors de l'envoi de l'email: {str(e)}"
    

    