from brahmastra.prebuild_tool import YoutubeSearchTool, WikipediaSearchTool, YoutubeTranscriptTool
from brahmastra.llm_agent import Create_ReAct_Agent, Create_MultiToolAgent, Create_ToolCalling_Agent
from brahmastra.core import Tool
from brahmastra.prebuild_autonomous_tool import PSExecTool, PSGenTool
from brahmastra.llm_provider import GoogleLLM

# Or create with API key directly (Option 2: Pass API key)
youtube = YoutubeSearchTool(api_key="AIzaSyCsJ5cmln2krNCgB3kq7rjmeHfzfA4zU20")
Wikipedia = WikipediaSearchTool()
transcript_tool = YoutubeTranscriptTool()
psexec_tool = PSExecTool()

def calculator(expression: str) -> str:
    """Performs mathematical calculations on expressions."""
    try:
        result = eval(expression)
        return f"Result: {result}"
    except Exception as e:
        return f"Error: {str(e)}"



# Create agent - using ReAct for better reasoning
llm1 = GoogleLLM(model="gemini-3-pro-preview")
llm = GoogleLLM(model="gemini-2.5-flash")
agent = Create_MultiToolAgent(
    llm=llm, 
    verbose=True,
    agent_introduction="You are designed by Aman"
)

psgen_tool = PSGenTool(llm=llm1)
# Add tools to agent
agent.add_tools(calculator, Wikipedia, youtube, transcript_tool, psexec_tool, psgen_tool)


# Run queries
# Note: "decrease brightness by 20%" is inherently SEQUENTIAL (need current value first)
# Use this query to test PARALLEL execution:
query = "who are you"

# For sequential tasks like brightness, the agent correctly uses sequential mode:
# query = "decrease system brightness by 20%"

result = agent.invoke(query)