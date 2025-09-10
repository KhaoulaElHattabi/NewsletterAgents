import os
from crewai import Agent
from datetime import datetime, timedelta
from crewagents.llm_integration import llm
from tool import send_newsletter
from crewai_tools import SerperDevTool


current_date = datetime.now()
start_week = (current_date - timedelta(days=current_date.weekday())).strftime('%Y-%m-%d')  # Monday of the current week
end_week = (current_date + timedelta(days=(6 - current_date.weekday()))).strftime('%Y-%m-%d')  # Sunday of the current week
numbers_of_articles = 5


os.environ.get("SERPER_API_KEY")
search_tool = SerperDevTool()


# Optimize agent definitions
researcher = Agent(
    role='AI News Researcher',
    goal='Find the latest AI developments',
    backstory=f"""You're an AI researcher focusing on getting {numbers_of_articles} news articles and breakthroughs from {start_week} to {end_week}. 
    If no results, search 7 days before {start_week}.""",
    tools=[search_tool],
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
    tools=[send_newsletter()],
    verbose=True,
    llm=llm
)
