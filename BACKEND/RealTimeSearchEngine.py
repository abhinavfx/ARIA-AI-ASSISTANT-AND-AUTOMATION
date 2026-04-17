from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

# =========================
# Load Environment Variables
# =========================
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# =========================
# Initialize Groq Client
# =========================
client = Groq(api_key=GroqAPIKey)

# =========================
# System Instruction Message
# =========================
System = f"""***Hello, I am {Username}, your creator and owner.
I built you from scratch. You're my personal AI assistant.
I am a BTech 3rd-year student at SRIT University, passionate about AI, ML, and DL.
You are {Assistantname}, an intelligent assistant with real-time search capabilities.
Always reply professionally using correct grammar and punctuation.***"""

# =========================
# Chat Log Initialization
# =========================
try:
    with open(r"Data\ChatLog.json") as f:
        messages = load(f)
except:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

# =========================
# Google Search Function
# =========================
def GoogleSearch(Query):
    """Fetches the top 5 search results from Google."""
    try:
        results = []
        for i in search(Query, num=5):
            results.append(i)

        if not results:
            return f"No search results found for '{Query}'."

        Answer = f"The top search results for '{Query}' are:\n[start]\n"
        for idx, link in enumerate(results, 1):
            Answer += f"{idx}. {link}\n"
        Answer += "[end]"
        return Answer
    except Exception as e:
        return f"⚠️ Search Error: {e}"

# =========================
# Clean the AI’s Response
# =========================
def AnswerModifier(Answer):
    """Removes empty lines and cleans up the AI response."""
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    return "\n".join(non_empty_lines)

# =========================
# Default System Messages
# =========================
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": f"Hello {Username}! How can I help you today?"}
]

# =========================
# Real-Time Info Function
# =========================
def Information():
    """Provides current real-time information for context."""
    now = datetime.datetime.now()
    return f"""Use this real-time info if needed:
Day: {now.strftime('%A')}
Date: {now.strftime('%d %B %Y')}
Time: {now.strftime('%H:%M:%S')}
"""

# =========================
# Real-Time Search Engine
# =========================
def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    # Load chat history
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)

    # Keep only the last few messages to avoid token overload
    if len(messages) > 8:
        messages = messages[-8:]

    # Add user input
    messages.append({"role": "user", "content": prompt})

    # Perform Google Search (limit to short output)
    search_results = GoogleSearch(prompt)
    if len(search_results) > 800:  # limit to 800 chars to avoid token overflow
        search_results = search_results[:800] + " ... [truncated]"

    SystemChatBot.append({"role": "system", "content": search_results})

    # Add date and time info
    system_info = Information()
    SystemChatBot.append({"role": "system", "content": system_info})

    # Merge all context messages
    full_context = SystemChatBot + messages

    # Clean empty messages
    full_context = [msg for msg in full_context if msg.get("content")]

    # Generate AI response
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=full_context,
        temperature=0.7,
        max_tokens=1500,  # reduce token generation limit
        top_p=1,
        stream=True,
    )

    Answer = ""
    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    # Clean the response
    Answer = Answer.strip().replace("</s>", "")

    # Save new chat to log
    messages.append({"role": "assistant", "content": Answer})
    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f, indent=4)

    return AnswerModifier(Answer)


# =========================
# Run in Terminal
# =========================
if __name__ == "__main__":
    while True:
        prompt = input("Enter Your Query :- ")
        if prompt.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break
        print(RealtimeSearchEngine(prompt))
