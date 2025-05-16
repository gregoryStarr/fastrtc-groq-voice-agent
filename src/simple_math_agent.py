from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from loguru import logger

model = ChatGroq(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    max_tokens=512,
)


def sum_numbers(a: float, b: float) -> float:
    """Sum two numbers together."""
    result = a + b
    logger.info(f"➕ Calculating sum: {a} + {b} = {result}")
    return result


def multiply_numbers(a: float, b: float) -> float:
    """Multiply two numbers together."""
    result = a * b
    logger.info(f"✖️ Calculating product: {a} × {b} = {result}")
    return result


tools = [sum_numbers, multiply_numbers]

system_prompt = """You are Samantha, a helpful math assistant with a warm personality.
You can help with basic math operations by using your tools.
Always use the tools when asked to do math calculations.
Your output will be converted to audio so avoid using special characters or symbols.
Keep your responses friendly and conversational."""

memory = InMemorySaver()

agent = create_react_agent(
    model=model,
    tools=tools,
    prompt=system_prompt,
    checkpointer=memory,
)

agent_config = {"configurable": {"thread_id": "default_user"}}
