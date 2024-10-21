from crewai import Crew, Process
from crewai_agents.agents import researcher, writer, editor, sender
from crewai_agents.tasks import research_task, content_generation_task, newsletter_structure_task, sending_task
from crewai_agents.tool import send_newsletter
from crewai_agents.azure_llm import llm
from crewai_agents.newsletter_template import NEWSLETTER_TEMPLATE

__all__ = [
    'researcher',
    'writer',
    'editor',
    'sender',
    'research_task',
    'content_generation_task',
    'newsletter_structure_task',
    'sending_task',
    'send_newsletter',
    'llm',
    'NEWSLETTER_TEMPLATE',
    'tavily_tool'
]

