from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from app.models.state import State
# Import tools
from app.services.tools import (
    recommend_products,
    place_order,
    check_order_status,
    analyze_skin_before_recommed,
    get_store_info
)

# Initialize Graph
graph_builder = StateGraph(State)
memory = MemorySaver()

# Initialize LLM
llm = ChatOpenAI(model="gpt-4o-mini",tempreture = 0.1).bind(system="""
You are Skincare Specialist Assistant. Your role is to analyze users' skin concerns and recommend suitable products.  

### **Responsibilities:**  
1. **Skin Analysis:**  
   - Gather details about the user's skin concerns, type, routine, and preferences.  
   - Use `analyze_skin_before_recommend` to assess their skin before making recommendations.  

2. **Product Suggestions:**  
   - Use `recommend_product` to suggest suitable skincare items.  
   - If a user requests products, provide recommendations.  
   - If a user has a skincare issue, suggest a complete product set with usage instructions.  

3. **Strict Focus on Skincare:**  
   - If greeted, introduce yourself and explain how you can help.  
   - Always gather relevant details before analyzing the user's skin.  
   - **If the user asks anything unrelated to skincare, do NOT attempt to answer. Instead, firmly but politely respond:**  
     _"I specialize in skincare and can only help with skin-related concerns. Let me know if you need skincare advice!"_
   - **Avoid engaging in off-topic discussions under any circumstances.**  
""")





# Define tools
skincare_tools = [
    analyze_skin_before_recommed,
    recommend_products,
    place_order,
    check_order_status,
    get_store_info
]

llm_with_tools = llm.bind_tools(skincare_tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# Add chatbot node
graph_builder.add_node("chatbot", chatbot)

# Tool Node for executing skincare-related tools
tool_node = ToolNode(tools=skincare_tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges("chatbot", tools_condition)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

# Compile the graph
graph = graph_builder.compile(checkpointer=memory)

# Function to run chatbot
def run_chatbot(user_input: str, thread_id: str):
    try:
        # Create the state with user input
        state = {"messages": [HumanMessage(content=user_input)]}
        config = {"configurable": {"thread_id": thread_id}}

        # Invoke the chatbot
        response = graph.invoke(state, config=config)

        # Ensure response contains messages
        if not response or "messages" not in response:
            raise ValueError("Invalid response format from graph.invoke")
        
        return {"bot_message": response}

    except Exception as e:
        raise ValueError(f"Chatbot processing error: {str(e)}")
