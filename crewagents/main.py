from crewai import Crew, Process
from agents import researcher, writer, editor, sender
from tasks import research_task, content_generation_task, newsletter_structure_task, sending_task
# Load environment variables
from dotenv import load_dotenv
import signal
import sys


def main():
    load_dotenv()

    newsletter_crew = Crew(
        agents=[researcher, writer, editor, sender],
        tasks=[research_task, content_generation_task, newsletter_structure_task, sending_task],
        verbose=True,
        process=Process.sequential,
    )

    result = newsletter_crew.kickoff()
    print("Crew result:", result)

def signal_handler(sig, frame):
    print('Stopping CrewAI workflow...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    main()
    signal_handler(signal.SIGINT, None)

