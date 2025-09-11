from crewai import Task
from agents import researcher, writer, editor, sender
from newsletter_template import NEWSLETTER_TEMPLATE
from datetime import datetime, timedelta

numbers_of_articles = 5
current_date = datetime.now()

# Define tasks
research_task = Task(
    description=f"Search for the latest {numbers_of_articles} AI developments using Tavily. Focus on recent breakthroughs and significant updates.",
    agent=researcher,
    expected_output=f"A list of {numbers_of_articles} recent AI articles with titles and URLs.",
    max_retries=1

)

content_generation_task = Task(
    description=f"""For each of the {numbers_of_articles} articles:
    1. Generate a catchy French title (in quotes)
    2. Write a 2-3 sentence summary in French
    3. Include the source link
    Do not use emoji characters.""",
    agent=writer,
    expected_output=f"{numbers_of_articles} résumés d'articles avec titres accrocheurs en français et liens sources",
    context=[research_task]
)



newsletter_structure_task = Task(
 description=f"""Structure the newsletter using the generated content. Use the following HTML template and fill it with the appropriate content:

{NEWSLETTER_TEMPLATE}


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
