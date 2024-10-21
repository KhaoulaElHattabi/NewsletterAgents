import ast
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
import os
from langchain_openai import AzureChatOpenAI
from typing import Any, Dict, TypedDict, List
from langchain_core.agents import AgentAction
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
import ast
from langchain_core.utils.function_calling import convert_to_openai_function
from langgraph.prebuilt import ToolExecutor, ToolInvocation    
from langchain_core.messages import HumanMessage, AIMessage


load_dotenv()


"""
#agent
class AgentState(TypedDict):
    #input: str
    chat_history: list[BaseMessage] #chat history
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add] #add every tool used

"""

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
    intro_message = generate_with_llm("","Génère une introduction engageante pour une newsletter sur les avancées en intelligence artificielle.")  # Introduction dynamique

    formatted_newsletter = [newsletter_title, intro_message, ""] 
    
    for article in article_summaries:
        content = article['content']
        url = article['url']
        
        # Génération d'un titre et résumé avec LLM
        title =generate_with_llm(content, "Peux-tu générer un titre accrocheur pour cet article : {}")
        summary = generate_with_llm(content, "Peux-tu générer un résumé de cet article : {}")
        
        # Construction de la section de la newsletter
        newsletter_section = (
            f"{title} 🎉\n\n"
            f"{summary} 😎\n"
            f"🔗 Découvrez tous les détails ici : {url}\n\n"
            "💡---------------------💡\n"
        )
        formatted_newsletter.append(newsletter_section)
    
    ending_message = generate_with_llm("","Génère une conclusion dynamique, amicale et engageante en 2 phrases pour une newsletter sur les avancées en intelligence artificielle.")
    
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

"""# Modify the system prompt to include instructions for using sendmail_tool
system_prompt = 
You are the newsletter maven, the great AI newsletter maker. Use the Tavily search tool to collect relevant information. Once you have collected enough information, you must use the final_answer tool to generate a formatted newsletter based on the collected articles. Finally, use the sendmail_tool to send the newsletter via email. Remember:

1. Use the final_answer tool only once for each newsletter.
2. Aim to collect diverse information to provide a comprehensive response.
3. Be creative and engaging in your newsletter content.
4. Ensure the newsletter is well-formatted and easy to read.
5. Provide a clear and concise summary of the collected articles.
6. After generating the newsletter, always use the sendmail_tool to send it.

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

     # Register the sendmail tool here
}"""

class AgentState(Dict[str, Any]):
    input: str
    chat_history: List[HumanMessage | AIMessage]
    steps: List[Dict[str, Any]]
    plan: List[str]

# Define the planning prompt
planner_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a planner for a newsletter creation. 
    Your task is to create a plan to gather information, create a newsletter, and send it via email.
    Available tools:
    1. tavily_search: Search for latest AI news
    2. final_answer: Generate a newsletter from search results
    3. sendmail_tool: Send the generated newsletter via email
    
    Provide a step-by-step plan using these tools."""),
    ("human", "{input}")
])

# Define the execution prompt
executor_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an executor for a newsletter creation.
    Your task is to execute the given plan step by step.
    Available tools:
    1. tavily_search: Search for latest AI news
    2. final_answer: Generate a newsletter from search results
    3. sendmail_tool: Send the generated newsletter via email
    
    Execute the current step of the plan."""),
    ("human", "Current plan: {plan}\nCurrent step: {current_step}\nPrevious steps: {steps}")
])


tools = [
    tavily_search,
    final_answer,
    sendmail_tool
]
tool_executor = ToolExecutor(tools)


# Define the planner
def plan(state):
    messages = planner_prompt.format_messages(input=state["input"])
    response = llm_model.invoke(messages)
    plan = response.content.split('\n')
    return {"plan": plan}

# Define the executor
def execute(state):
    current_step = state["plan"][len(state["steps"])]
    messages = executor_prompt.format_messages(
        plan=state["plan"],
        current_step=current_step,
        steps=state["steps"]
    )
    response = llm_model.invoke(messages)
    
    # Parse the response to get the tool and input
    # This is a simplified parsing, you might need to adjust based on your LLM's output format
    tool_name = response.content.split('(')[0].strip()
    tool_input = response.content.split('(')[1].split(')')[0].strip()
    
    # Execute the tool
    action = ToolInvocation(tool=tool_name, tool_input=tool_input)
    result = tool_executor.invoke(action)
    
    new_step = {
        "action": {
            "tool": tool_name,
            "tool_input": tool_input,
            "log": ""
        },
        "result": str(result)
    }
    
    return {"steps": state["steps"] + [new_step]}

# Define the condition to end the execution
def should_end(state):
    return len(state["steps"]) == len(state["plan"])

# Create the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("planner", plan)
workflow.add_node("executor", execute)

# Add edges
workflow.set_entry_point("planner")
workflow.add_edge("planner", "executor")
workflow.add_edge("executor", "executor")

# Add conditional edge to end
workflow.add_conditional_edges(
    "executor",
    should_end,
    {
        True: END,
        False: "executor"
    }
)

# Compile the graph
app = workflow.compile()

# Run the agent
inputs = {
    "input": "Create and send a newsletter about the latest AI developments",
    "chat_history": [],
    "steps": [],
    "plan": []
}

for output in app.stream(inputs):
    if "__end__" not in output:
        print(output)
    else:
        print("\nFinal output:", output)




"""
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

if __name__ == "__main__":
    # Example of the query to start the agent
    query = "latest AI news"
    
    # Start the agent with the initial search state
    initial_state = AgentState(
        chat_history=[system_message],  # Include system prompt in the initial chat history
        intermediate_steps=[AgentAction(tool="tavily_search", tool_input=query, log="Starting Tavily search")]
    )
    output_state = runnable.invoke(initial_state)

    # Print the final state to see the results
    print("Final state:")
    for step in output_state["intermediate_steps"]:
        print(f"Tool: {step.tool}")
        print(f"Input: {step.tool_input}")
        print(f"Output: {step.log}")
        print("---")
"""
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
    