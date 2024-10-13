import ast
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
import os
from langchain_openai import AzureChatOpenAI
from typing import Any, Dict, TypedDict, Annotated, List
from langchain_core.agents import AgentAction
from langchain_core.messages import BaseMessage
import operator
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder




load_dotenv()

llm_model = AzureChatOpenAI(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        model=os.getenv("OPENAI_CHAT_MODEL"),
        api_version=os.getenv("API_VERSION"),
        azure_endpoint=os.getenv("API_BASE"),
        temperature=0
    )

#agent
class AgentState(TypedDict):
    #input: str
    chat_history: list[BaseMessage] #chat history
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add] #add every tool used


@tool("tavily_search")
def tavily_search(query: str) -> List[Dict[str, Any]]:
    """test"""
    # Perform Tavily search
    print(f"Performing Tavily search with query: {query}")

    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        raise ValueError("TAVILY_API_KEY not found. Please add it as an environment variable.")
    
    search = TavilySearchResults(
        tavily_api_key=tavily_api_key,
        max_results=5,
        include_domains=["wikipedia.org"]
    )
    results = search.invoke(query)
    
    # Ensure results are returned as a list of dicts
    formatted_results = []
    for result in results:
        formatted_results.append({
            "url": result.get("url", ""),
            "content": result.get("content", "")
        })
    
    return formatted_results


@tool("final_answer")
def final_answer(article_summaries: List[Dict[str, str]]) -> str:
    """
    Génère un bulletin de nouvelles créatif et amical avec des titres, des résumés et des emojis pour chaque article.
    L'introduction et la conclusion sont dynamiquement générées par un LLM.
    """
    print(f"Generating final answer based on: {article_summaries}")

    newsletter_title = "📰 GenAI Info est là - Votre GenAI newsletter hebdomadaire 📰\n\n"  # Titre stylisé
    intro_message = generate_dynamic_intro()

    formatted_newsletter = [newsletter_title, intro_message, ""] 
    
    for article in article_summaries:
        content = article['content']
        url = article['url']
        
        # Génération d'un titre et résumé avec LLM
        title = generate_title_with_llm(content)
        summary = generate_summary_with_llm(content)
        
        # Construction de la section de la newsletter
        newsletter_section = (
            f"{title} 🎉\n\n"
            f"{summary} 😎\n"
            f"🔗 Découvrez tous les détails ici : {url}\n\n"
            "💡---------------------💡\n"
        )
        formatted_newsletter.append(newsletter_section)
    
    ending_message = generate_dynamic_ending()
    
    formatted_newsletter.append(ending_message)
    
    return "\n".join(formatted_newsletter)


def generate_with_llm(content : str, prompt: str) -> str:
    """
    Génère un texte créatif et engageant en utilisant un LLM.
    """
    messages = [{"role": "user",
                 "content": prompt.format(content)}]
    try:
        response = llm_model.generate(messages=[messages])
        
        generated_text = response.generations[0][0].text.strip()
        return generated_text
    except Exception as e:
        print(f"Error generating text with LLM: {e}")
        return ""

def generate_dynamic_intro() -> str:
    """
    Génère une introduction créative et dynamique pour la newsletter en utilisant un LLM.
    """
    return generate_with_llm("","Génère une introduction dynamique, amicale et engageante en 2 phrase pour une newsletter sur les avancées en intelligence artificielle.")

def generate_dynamic_ending() -> str:
    """
    Génère une conclusion créative et dynamique pour la newsletter en utilisant un LLM.
    """

    return generate_with_llm("","Génère une conclusion dynamique, amicale et engageante en 2 phrases pour une newsletter sur les avancées en intelligence artificielle.")

def generate_title_with_llm(content: str) -> str:
    """
    Génère un titre accrocheur à partir du contenu de l'article en utilisant un LLM.
    """
    return generate_with_llm(content, "Peux-tu générer un titre accrocheur pour cet article : {}")

def generate_summary_with_llm(content: str) -> str:
    """
    Génère un résumé d'un contenu d'article en utilisant un modèle LLM.
    """
    return generate_with_llm(content, "Peux-tu générer un résumé de cet article : {}")


def send_email(subject, body, to_email, from_email, password):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
 
    server = None
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.sendmail(from_email, to_email, msg.as_string())
        return "Email envoyé avec succès!"
    except Exception as e:
        return f"Erreur lors de l'envoi de l'email: {e}"
    finally:
        if server is not None:
            server.quit()
 
@tool("sendmail_tool")
def sendmail_tool(body: str) -> str:
    """
    Sends an email with the provided body content.
    """
    print(f"Preparing to send email with body: {body}")

    from_email = os.getenv("FROM_EMAIL")
    password = os.getenv("EMAIL_PASSWORD")
    to_email = os.getenv("TO_EMAIL")
    return send_email(subject="GenAI Newsletter", body=body, to_email=to_email, from_email=from_email, password=password)

system_prompt = """
You are the newsletter maven, the great AI newsletter maker.
Use the Tavily search tool to collect relevant information. 
Once you have collected enough information, you must use the `final_answer` tool to generate a formatted newsletter based on the collected articles. 
Finally, prepare the newsletter to be sent via email.
Remember:
- Use the `final_answer` tool only once for each newsletter.
- Aim to collect diverse information to provide a comprehensive response.
- Be creative and engaging in your newsletter content.
- Ensure the newsletter is well-formatted and easy to read.
- Provide a clear and concise summary of the collected articles.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="chat_history")
])


# Define a system message, ensuring the 'type' field is included
system_message = BaseMessage(
    content=system_prompt,
    role="system",
    type="text"  # Explicitly define the 'type' field
)

tool_str_to_func = {
    "tavily_search": tavily_search,
    "final_answer": final_answer,
    "sendmail_tool": sendmail_tool        # Register the sendmail tool here
}

from langgraph.graph import StateGraph, END
import ast

def run_tool(state: dict):
    # Simplified tool runner based on intermediate steps
    tool_name = state["intermediate_steps"][-1].tool
    tool_args = state["intermediate_steps"][-1].tool_input
    print(f"{tool_name}.invoke(input={tool_args})")
    
    # Run the appropriate tool based on the tool name
    output = tool_str_to_func[tool_name](tool_args)
    print(f"Tool output: {output}")

    
    # Log the tool output and return the updated state
    action_out = AgentAction(tool=tool_name, tool_input=tool_args, log=str(output))
    return {"intermediate_steps": [action_out]}


# Create the state graph
graph = StateGraph(AgentState)

# Add nodes for each tool
graph.add_node("tavily_search", run_tool)
graph.add_node("final_answer", run_tool)
graph.add_node("sendmail_tool", run_tool)

# Set the entry point
graph.set_entry_point("tavily_search")

# Add edges to define the flow between tools
# Since the router is removed, we'll explicitly define the next tool for each step.
graph.add_edge("tavily_search", "final_answer")
graph.add_edge("final_answer", "sendmail_tool")  # After generating the newsletter, send the email
graph.add_edge("sendmail_tool", END)  # End after sending the email

# Compile the graph into a runnable agent
runnable = graph.compile()

# Example usage of the agent
if __name__ == "__main__":
    # Example of the query to start the agent
    query = "latest AI news"
    
    # Start the agent with the initial search state
    initial_state = AgentState(
        chat_history=[system_message],  # Include system prompt in the initial chat history
        intermediate_steps=[AgentAction(tool="tavily_search", tool_input=query, log="Starting Tavily search")]
    )
    output_state = runnable.invoke(initial_state)

"""
class Agent:
    def __init__(self):
        self.state = {
            "intermediate_steps": [],
            "chat_history": []  # Initialisation de l'historique de conversation
        }

    def run(self):
        # Ajouter le system prompt dans l'historique de conversation
        self.state["chat_history"].append({"role": "system", "content": system_prompt})
        
        # Step 1: Perform search using Tavily Search
        self.state["intermediate_steps"].append({
            "tool": "tavily_search",
            "tool_input": {"query": "Quelles sont les dernières avancées en intelligence artificielle et l'IA générative ?"}
        })
        self.state = run_tool(self.state)
        
        
        # Step 2: Process search results with final_answer
        search_results = self.state["intermediate_steps"][-1]["log"] 
        if isinstance(search_results, str):
            search_results = ast.literal_eval(search_results)  # Convert string to list of dicts

    # Get the search results from the previous tool
        if search_results:
            self.state["intermediate_steps"].append({
                "tool": "final_answer",
                "tool_input": {"article_summaries": search_results}
            })
            self.state = run_tool(self.state)
        
        # Step 3: Send email with the generated newsletter
        newsletter_content = self.state["intermediate_steps"][-1]["log"]
        if newsletter_content:
            self.state["intermediate_steps"].append({
                "tool": "sendmail_tool",
                "tool_input": {"body": newsletter_content}
            })
            self.state = run_tool(self.state)
        
        return self.state

# Fonction pour exécuter un outil
def run_tool(state: dict):
    tool_name = state["intermediate_steps"][-1]["tool"]
    tool_args = state["intermediate_steps"][-1]["tool_input"]
    
    #print(f"Invoking tool: {tool_name} with input: {tool_args}")
    
    # Appeler l'outil en fonction du nom
    if tool_name in tool_str_to_func:
        out = tool_str_to_func[tool_name](tool_args)
    else:
        raise ValueError(f"Tool {tool_name} not found in tool_str_to_func")
    
    # Capture the result in 'log'
    action_out = AgentAction(
        tool=tool_name,
        tool_input=tool_args,
        log=str(out)  # Make sure the result is stored in log
    )
    
    # Add the result to the state
    state["intermediate_steps"][-1]["log"] = action_out.log  # Store 'log' properly
    
    return state



# Example usage of the agent
if __name__ == "__main__":
    agent = Agent()
    final_state = agent.run()"""
    