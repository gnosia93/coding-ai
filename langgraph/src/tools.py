from langchain.tools import tool 
from langchain.chat_models import init_chat_model 

model = init_chat_model(
    "global.anthropic.claude-sonnet-4-6",
    model_provider="bedrock_converse",
    temperature = 0, 
)

1
@tool
def multiply(a: int, b: int) -> int:
    """Multiply `a` and `b`.P
    
    Args:
        a: First int
        b: Second int 
    """
    return a * b

@tool 
def add(a: int, b: int) -> int: 
    """Add `a` and `b`.
    
    Args:
        a: First int
        b: Second int 
    """
    return a + b

@tool 
def divide(a: int, b: int) -> int:
    """Divide `a` and `b`.
    
    Args:
        a: First int
        b: Second int 
    """
    return a / b

tools = [add, multiply, divide]
tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = model.bind_tools(tools)


from langchain.messages import AnyMessage
from typing_extensions import TypedDict, Annotated 
import operator 

class MessagesState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int 

from langchain.messages import SystemMessage 

def llm_call(state: dict):
    """ LLM decides whether to call a tool or not """

    return {
        "messages": [
            model_with_tools.invoke( [
                SystemMessage(
                    content = "You are a helpful assitant tasked with performing arithmetic on a set of inputs." 
                )
            ] + state["messages"] )
        ],
        "llm_calls": state.get('llm_calls', 0) + 1
    }


from langchain_core.messages import ToolMessage

def tool_node(state: dict):
    
    """
    # LLM이 뱉어낸 tool_calls의 대략적인 모습
    {
        "id": "call_abc123",            # 이 요청의 고유 ID
        "name": "get_weather",          # 실행하라고 지정한 함수 이름
        "args": {"location": "Seoul"}   # 함수에 넘겨줄 파라미터 값
    }
    """

    result = []
    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]
        observation = tool.invoke(tool_call["args"])
        result.append(ToolMessage(content=observation, tool_call_id=tool_call["id"]))
    return {"messages": result}


from typing import Literal 
from langgraph.graph import StateGraph, START, END 
from langchain_core.messages import AIMessage 

def should_continue(state: MessagesState) -> Literal["tool_node", END]:
    last_message = state["messages"][-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tool_node"
    
    return END


agent_builder = StateGraph(MessagesState)
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("tool_node", tool_node) 

agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call", 
    should_continue,
    ["tool_node", END]
)
agent_builder.add_edge("tool_node", "llm_call")

agent = agent_builder.compile()

                                   
# show the agent 
from IPython.display import Image, display 
display(Image(agent.get_graph(xray=True).draw_mermaid_png()))


# Invoke
from langchain.messages import HumanMessage 
messages = [ HumanMessage(content="Add 3 and 4.") ]
messages = agent.invoke({"messages": messages})
for m in messages["messages"]:
    m.pretty_print()







