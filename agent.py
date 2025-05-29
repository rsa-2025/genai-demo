from langchain_openai import ChatOpenAI
from langchain.agents import tool, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents.format_scratchpad.openai_tools import format_to_openai_tool_messages
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
import yfinance as yf

# === TOOL: Screener ===
@tool
def screen_stocks(scr_ids: list = ["most_actives"], count: int = 5):
    """
    Uses yfinance's screener to fetch top tickers for investment insight.
    
    Args:
        scr_ids (list): List of screener IDs like 'most_actives', 'day_gainers', 'day_losers'.
        count (int): Number of top stocks to return.
        
    Returns:
        str: Formatted summary of top screen results.
    """
    try:
        data = yf.screener(scr_ids=scr_ids, count=count)
        results = []
        for scr_id, df in data.items():
            top_stocks = df.head(count)
            summary = f"\nTop {count} from '{scr_id}':\n" + top_stocks[['symbol', 'shortName', 'regularMarketPrice']].to_string(index=False)
            results.append(summary)
        return "\n\n".join(results)
    except Exception as e:
        return f"Error using screener: {str(e)}"

# === PROMPTS ===
analysis_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an AI stock analyst. Use your tools to analyze stocks and respond with data-backed insights. Always run code to justify answers."""),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

advice_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an investment advisor. Use stock screeners and any available tools to suggest investment opportunities. Justify all recommendations using real data from yfinance.screener."""),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# === LLM SETUP ===
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# === TOOLS ===
tools = [screen_stocks]

# === AGENT EXECUTORS ===
analysis_agent_executor = AgentExecutor(
    agent=(lambda x: {"input": x["input"], "agent_scratchpad": format_to_openai_tool_messages(x["intermediate_steps"])})
           | analysis_prompt
           | llm.bind_tools(tools)
           | OpenAIToolsAgentOutputParser(),
    tools=tools,
    verbose=True
)

advice_agent_executor = AgentExecutor(
    agent=(lambda x: {"input": x["input"], "agent_scratchpad": format_to_openai_tool_messages(x["intermediate_steps"])})
           | advice_prompt
           | llm.bind_tools(tools)
           | OpenAIToolsAgentOutputParser(),
    tools=tools,
    verbose=True
)
