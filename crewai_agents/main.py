import base64
import os
from crewai import LLM, Agent, Task, Crew, Process
from langchain_openai import AzureChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools import tool
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import smtplib
from datetime import datetime, timedelta
from PIL import Image
import io

# Set up Azure OpenAI
llm = LLM(
    model="azure/gpt4-TURBO",
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("API_BASE")
)



numbers_of_articles = 5
current_date = datetime.now()
start_week = (current_date - timedelta(days=current_date.weekday())).strftime('%Y-%m-%d')  # Monday of the current week
end_week = (current_date + timedelta(days=(6 - current_date.weekday()))).strftime('%Y-%m-%d')  # Sunday of the current week


api_key=os.getenv("TAVILY_API_KEY")
tavily_wrapper = TavilySearchAPIWrapper(tavily_api_key=api_key)

tavily_tool = TavilySearchResults(
    max_results=numbers_of_articles,
    exclude_domains=["wikipedia.org"],
    api_wrapper=tavily_wrapper
)

@tool("Newsletter Emailer")

def send_newsletter(body: str) -> str:
    """Send the generated newsletter via email."""
    try:
        msg = MIMEMultipart()
        msg['From'] = os.getenv("FROM_EMAIL")
         # Get the list of recipient emails with error handling
        to_emails = os.getenv("TO_EMAILS")
        if not to_emails:
            return "Erreur: TO_EMAILS n'est pas défini dans les variables d'environnement."
        
        recipients = [email.strip() for email in to_emails.split(',') if email.strip()]
        
        if not recipients:
            return "Erreur: Aucune adresse email valide trouvée dans TO_EMAILS."
        
        msg['Subject'] = Header("GenAI Newsletter", 'utf-8')
        body_images={"my_image": "./banner.jpg"}

        # Encode the body as UTF-8
        msg.attach(MIMEText(body.encode('utf-8'), 'html', 'utf-8'))
        
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=60) as server:
            server.set_debuglevel(1)  # Enable debug output
            server.starttls()
            server.login(os.getenv("FROM_EMAIL"), os.getenv("EMAIL_PASSWORD"))
            server.send_message(msg)
        return "Email envoyé avec succès!"
    except smtplib.SMTPException as e:
        return f"Erreur SMTP lors de l'envoi de l'email: {str(e)}"
    except Exception as e:
        return f"Erreur lors de l'envoi de l'email: {str(e)}"
    
    print(body)  # Ajoutez ceci juste avant d'envoyer l'email
    
# Optimize agent definitions
researcher = Agent(
    role='AI News Researcher',
    goal='Find the latest AI developments',
    backstory=f"""You're an AI researcher focusing on news and breakthroughs from {start_week} to {end_week}. 
    If no results, search 7 days before {start_week}.""",
    tools=[tavily_tool],
    verbose=True,
    llm=llm
)

writer = Agent(
    role='Newsletter Writer',
    goal='Create an engaging AI newsletter',
    backstory="You're a skilled writer who can create compelling newsletters about AI advancements in French.",
    verbose=True,
    llm=llm
)
editor = Agent(
    role='Newsletter Editor',
    goal='Structure and format the newsletter',
    backstory="You're an experienced editor who can organize content into an engaging newsletter format.",
    verbose=True,
    llm=llm
)
sender = Agent(
    role='Email Sender',
    goal='Send the newsletter via email',
    backstory="You're responsible for sending out the newsletter to subscribers.",
    tools=[send_newsletter],
    verbose=True,
    llm=llm
)

# Define tasks
research_task = Task(
    description=f"Search for the latest {numbers_of_articles} AI developments using Tavily. Focus on recent breakthroughs and significant updates.",
    agent=researcher,
    expected_output=f"A list of {numbers_of_articles} recent AI articles with titles and URLs."
)
content_generation_task = Task(
    description=f"""For each of the {numbers_of_articles} articles:
    1. Generate a catchy French title (in quotes)
    2. Write a 2-3 sentence summary in French
    3. Include the source link
    Do not use emoji characters.""",
    agent=writer,
    expected_output=f"{numbers_of_articles} articles with French title, summary, and source link."
)

newsletter_structure_task = Task(
    description=f"""Structure the newsletter using the generated content. Use the following HTML template and fill it with the appropriate content:

<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GenAI Info est là - Votre newsletter hebdomadaire</title>
<style>
    body {{
        font-family: Arial, sans-serif;
        font-size: 16px;
        margin: 0;
        padding: 0;
        color: #333;
    }}
    .newsletter-container {{
        width: 100%;
        max-width: 600px;
        margin: 0 auto;
        padding: 20px;
    }}
    .article-summary {{
        margin-bottom: 30px;
    }}
    .article-summary h2 {{
        font-size: 20px;
        color: #0073AA;
    }}
    .article-summary p {{
        margin: 0;
        color: #666;
    }}
    .article-summary a {{
        color: #0073AA;
        text-decoration: none;
    }}
    .header-image {{
        width: 100%;
        max-width: 600px;
        height: auto;
        display: block;
        margin: 0 auto 20px;
    }}
    .footer {{
        text-align: center;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #ddd;
        font-size: 14px;
    }}
    .footer p {{
        margin: 0;
    }}
</style>
</head>
<body>
<div class="newsletter-container">

<img src={{my_image.src}} alt="Newsletter Image" class="header-image">

<p>{{introduction}}</p>

{{article_summaries}}

<div class="footer">
    <p>{{conclusion}}</p>
</div>

</div>
</body>
</html>

Instructions for filling the template:
1. Replace {{introduction}} with an engaging introduction in French.
2. Replace {{article_summaries}} with the summaries of the articles. For each article, use the following structure:

<div class="article-summary">
    <h2>&#x1F4A1; {{article_title}}</h2>
    <p>{{article_summary}}</p>
    <a href="{{article_link}}" target="_blank">Lire l'article complet</a>
</div>

3. Replace {{conclusion}} with a brief conclusion in French.
4. Ensure all text is properly HTML-encoded to avoid any rendering issues.
5. Use the following HTML entities for emojis:
   - &#x1F4F0; for 📰 (newspaper)
   - &#x1F4A1; for 💡 (light bulb)
   - &#x2B50; for ⭐ (star)
   - &#x1F60E; for 😎 (smiling face with sunglasses)

6. Ensure the content is informative, engaging, and follows the specified format.
7. The total length of the email body should not exceed 100,000 characters. If it does, truncate the content appropriately while maintaining the structure.
8. Use different emojis for each article title to add variety.""",
    agent=editor,
    expected_output="A fully structured newsletter in HTML format, ready to be sent."
)


sending_task = Task(
    description="""Send the newsletter via email using the Newsletter Emailer tool:
    1. Verify HTML format
    2. Ensure proper HTML-encoding
    3. Use UTF-8 encoding
    4. If sending fails, print error and retry
    5. If second attempt fails, send a test email
    Report any issues encountered.""",
    agent=sender,
    expected_output="Email sending confirmation or error report."
)
# Optimize crew creation
newsletter_crew = Crew(
    agents=[researcher, writer, editor, sender],
    tasks=[research_task, content_generation_task, newsletter_structure_task, sending_task],
    verbose=True,
    process=Process.sequential,
    max_iterations=2  # Limit iterations for faster completion
)

# Run the crew
result = newsletter_crew.kickoff()
print("Crew result:", result)
"""
query = f"Latest AI developments {one_week_ago.strftime('%Y-%m-%d')} to {today.strftime('%Y-%m-%d')}"
results = tavily_tool(query)"""

