import streamlit as st
import os
import warnings
from dotenv import load_dotenv
from google import genai
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from google.genai import types

# Suppress warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

# Initialize Google client (will be done after API key check)
client = None

# Define State
class GameState(TypedDict):
    messages: Annotated[list, add_messages]
    order: list[str]
    finished: bool

# System instruction
GAMEBOT_SYSINT = (
    "system",
    "You are GameBot, an interactive board game expert system. A human will talk to you about "
    "various board games and you will answer any questions about game rules, strategies, and history "
    "(and only about board games - no off-topic discussion, but you can chat about the games and their history).\n\n"
    
    "You have access to the function `get_list_game()` to list available games.\n"
    "If a user asks about a game not in the list, do not tell them it's unavailable. "
    "Instead, print the game_name and call the `search_game_online(game_name)` tool to search online and help them.\n"
    
    "If the game is in your list (for example: 'Chess'), feel free to answer detailed questions about its rules, pieces, or strategy using your own knowledge.\n\n"
    
    "Be proactive and helpful. Respond in the user's language.\n"
    "Keep your responses concise and friendly.\n\n"
    
    "If any of the tools are unavailable, you can break the fourth wall and tell the user "
    "that they have not implemented them yet and should keep reading to do so."
)

WELCOME_MSG = "Welcome to the GameBot expert system! How may I assist you with board games today?"

# Define tools
@tool
def get_list_game() -> str:
    """Provide the latest up-to-date menu."""
    return """
    Game:
    Monopoly
    Scrabble
    Chess
    Cluedo
    Uno
    Mahjong
    Mikado
  """

@tool
def search_game_online(game_name: str) -> str:
    """Search online information about a board game if not found in the local list."""
    prompt = f"Can you give me a short description of the board game '{game_name}'?"
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
        ),
    )
    return response.candidates[0].content.parts[0].text

# Initialize LLM and tools
@st.cache_resource
def initialize_graph():
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
    tools = [get_list_game, search_game_online]
    tool_node = ToolNode(tools)
    llm_with_tools = llm.bind_tools(tools)
    
    def maybe_route_to_tools(state: GameState) -> Literal["tools", END]:
        if not (msgs := state.get("messages", [])):
            raise ValueError(f"No messages found when parsing state: {state}")
        msg = msgs[-1]
        if hasattr(msg, "tool_calls") and len(msg.tool_calls) > 0:
            return "tools"
        else:
            return END
    
    def chatbot_with_tools(state: GameState) -> GameState:
        defaults = {"order": [], "finished": False}
        if state["messages"]:
            new_output = llm_with_tools.invoke([GAMEBOT_SYSINT] + state["messages"])
        else:
            new_output = AIMessage(content=WELCOME_MSG)
        return defaults | state | {"messages": [new_output]}
    
    graph_builder = StateGraph(GameState)
    graph_builder.add_node("chatbot", chatbot_with_tools)
    graph_builder.add_node("tools", tool_node)
    
    graph_builder.add_conditional_edges("chatbot", maybe_route_to_tools)
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")
    
    return graph_builder.compile()

# Page config
st.set_page_config(
    page_title="GameBot - Board Game Expert",
    page_icon="🎲",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stChatMessage {
        background-color: blue;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.title("🎲 GameBot - Board Game Expert")
st.markdown("*Your AI assistant for board game rules, strategies, and history*")

# Check for API key early
if not GOOGLE_API_KEY:
    st.error("⚠️ Please set your GOOGLE_API_KEY in the .env file")
    st.info("Create a `.env` file with: `GOOGLE_API_KEY=your_api_key_here`")
    st.stop()

# Initialize client after API key check
client = genai.Client(api_key=GOOGLE_API_KEY)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.graph_state = {"messages": [], "order": [], "finished": False}

# Initialize graph
try:
    graph = initialize_graph()
except Exception as e:
    st.error(f"Error initializing the chatbot: {str(e)}")
    st.stop()

# Sidebar
with st.sidebar:
    st.header("ℹ️ About GameBot")
    st.markdown("""
    GameBot can help you with:
    - 📋 List of available games
    - 📖 Game rules and instructions
    - 🎯 Strategies and tips
    - 🔍 Search for games online
    
    **Available Games:**
    - Monopoly
    - Scrabble
    - Chess
    - Cluedo
    - Uno
    - Mahjong
    - Mikado
    """)
    
    if st.button("🔄 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.graph_state = {"messages": [], "order": [], "finished": False}
        st.rerun()

# Display welcome message if no messages
if len(st.session_state.messages) == 0:
    with st.chat_message("assistant", avatar="🎲"):
        st.markdown(WELCOME_MSG)

# Display chat messages
for message in st.session_state.messages:
    avatar = "🎲" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me about board games..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    
    # Add user message to graph state
    st.session_state.graph_state["messages"].append(HumanMessage(content=prompt))
    
    # Get bot response
    with st.chat_message("assistant", avatar="🎲"):
        with st.spinner("Thinking..."):
            try:
                config = {"recursion_limit": 100}
                result = graph.invoke(st.session_state.graph_state, config)
                st.session_state.graph_state = result
                
                # Get the last AI message
                last_message = result["messages"][-1]
                response = last_message.content
                
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_msg = f"Sorry, I encountered an error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'> First try on AI agent ! Have fun testing this application.😏</div>",
    unsafe_allow_html=True
)