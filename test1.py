
from brahmastra.llm_agent import Create_Reasoning_Agent
from brahmastra.llm_provider import GoogleLLM


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
agent = Create_Reasoning_Agent(
    llm=llm, 
    verbose=True,
)

# Run queries
query = "calculate (23 * 45) / 12 + 15 - 7"
result = agent.invoke(query)