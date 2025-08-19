from crewai import Crew, Process
from agents import researcher, writer, editor, sender
from tasks import research_task, content_generation_task, newsletter_structure_task, sending_task
# Load environment variables
from dotenv import load_dotenv


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

if __name__ == "__main__":
    main()

