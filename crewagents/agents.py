import os
from crewai import Agent
from datetime import datetime, timedelta
from llm_integration import llm
from tool import send_newsletter
from crewai_tools import SerperDevTool


current_date = datetime.now()
start_week = (current_date - timedelta(days=current_date.weekday())).strftime('%Y-%m-%d')  # Monday of the current week
end_week = (current_date + timedelta(days=(6 - current_date.weekday()))).strftime('%Y-%m-%d')  # Sunday of the current week
numbers_of_articles = 2
week_number = current_date.isocalendar()[1]  # ISO week number
print(f"Current week number: {week_number}")
print(f"Start week: {start_week}, End week: {end_week}")

os.environ.get("SERPER_API_KEY")
search_tool = SerperDevTool()


researcher = Agent(
    role='AI News Researcher',
    goal='Find the latest AI developments',
    backstory=f"""You're an AI researcher focusing on getting {numbers_of_articles} news articles and breakthroughs from {start_week} to {end_week}. 
    If no results, search 7 days before {start_week}.
    
    IMPORTANT: When using the search tool, pass only a simple string query, not a dictionary. 
    Example: Use "You're an AI researcher focusing on getting {numbers_of_articles} news articles and breakthroughs from {start_week} to {end_week}. 
    If no results, search 7 days before {start_week}. " not {{"search_query": "AI developments "}}""",
    tools=[search_tool],
    verbose=True,
    llm=llm,
    max_iter=1,
    allow_delegation=False,
    memory=True
)

writer = Agent(
    role='Newsletter Writer',
    goal='Create an engaging AI newsletter',
    backstory="You're a skilled writer who can create compelling newsletters about AI advancements in French.",
    verbose=True,
        max_iter=1,

    llm=llm
)

editor = Agent(
    role='Newsletter Editor',
    goal='Structure and format the newsletter',
    backstory="You're an experienced editor who can organize content into an engaging newsletter format.",
    verbose=True,
        max_iter=1,

    llm=llm
)

sender = Agent(
    role='Email Sender',
    goal='Send the newsletter via email',
    backstory="You're responsible for sending out the newsletter to subscribers.",
    tools=[send_newsletter()],
    verbose=True,
        max_iter=1,

    llm=llm
)
