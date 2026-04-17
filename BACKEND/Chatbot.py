from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables safely
env_vars = dotenv_values(".env")

# Ensure all environment variables are set
Username = env_vars.get("Username") or "User"
Assistantname = env_vars.get("Assistantname") or "Assistant"
GroqAPIKey = env_vars.get("GroqAPIKey")

# Ensure API key is provided
if not GroqAPIKey:
    raise ValueError("❌ Groq API Key is missing. Please check your .env file.")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# Default and backup models
PRIMARY_MODEL = "llama-3.3-70b-versatile"
BACKUP_MODEL = "mixtral-8x7b"

messages = []

System = (
    f"***Hello, I am {Username}, I am your owner and creator.*** "
    f"***I built you from scratch; you are my personal AI assistant. I am a BTech 3rd-year student of SRIT University and deeply passionate about AI, ML, and DL.*** "
    f"***My Father's name is Mukesh Vishwakarma, my Mother's name is Kirti Vishwakarma, my brother is Abhikansh Vishwakarma, and my sister is Aanya Vishwakarma.*** "
    f"***You are a very accurate and advanced AI chatbot named {Assistantname}, which can access real-time information.*** "
    f"***Do not tell time unless asked. Do not talk too much. Always answer in English. Do not mention your training data or show notes.***"
)

systemChatBot = [{"role": "system", "content": System}]

# Load chat history safely
try:
    with open("Data/ChatLog.json", "r") as f:
        messages = load(f)
except (FileNotFoundError, ValueError):
    with open("Data/ChatLog.json", "w") as f:
        dump([], f)
    messages = []

def RealtimeInformation():
    try:
        now = datetime.datetime.now()
        return (
            f"Day: {now.strftime('%A')}, Date: {now.strftime('%d %B %Y')}, "
            f"Time: {now.strftime('%H:%M:%S')}"
        )
    except Exception as e:
        print(f"❌ Error in RealtimeInformation: {e}")
        return "Real-time info unavailable."

def AnswerModifier(Answer):
    if not Answer:
        return "⚠️ No response received from AI."
    lines = Answer.split("\n")
    non_empty = [line.strip() for line in lines if line.strip()]
    return "\n".join(non_empty)

def ChatBot(Query, model_name=PRIMARY_MODEL):
    try:
        if not Query.strip():
            return "⚠️ Please enter a valid question."

        with open("Data/ChatLog.json", "r") as f:
            messages = load(f)

        messages.append({"role": "user", "content": Query})

        completion = client.chat.completions.create(
            model=model_name,
            messages=systemChatBot
            + [{"role": "system", "content": RealtimeInformation()}]
            + messages,
            max_tokens=8192,
            temperature=0.6,
            top_p=0.95,
            stream=True,
        )

        Answer = ""
        for chunk in completion:
            if hasattr(chunk.choices[0], "delta") and chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "").strip()
        messages.append({"role": "assistant", "content": Answer})
        with open("Data/ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer)

    except Exception as e:
        error_str = str(e)
        print(f"❌ ChatBot Error: {error_str}")

        # Handle model deprecation errors automatically
        if "model" in error_str and "decommissioned" in error_str:
            print(f"⚠️ Model {model_name} deprecated. Switching to backup model: {BACKUP_MODEL}")
            return ChatBot(Query, model_name=BACKUP_MODEL)

        # Handle Groq 400/404 gracefully
        if "Error code:" in error_str or "not found" in error_str:
            return "⚠️ AI model is temporarily unavailable. Try again later or check your API key."

        return "⚠️ An unknown error occurred. Please try again."

if __name__ == "__main__":
    print(f"🤖 {Assistantname} is ready! Type 'exit' or 'quit' to close.")
    while True:
        try:
            user_input = input("Enter Your Question: ").strip()
            if user_input.lower() in ["exit", "quit"]:
                print("👋 Exiting chatbot.")
                break
            print(ChatBot(user_input))
        except KeyboardInterrupt:
            print("\n👋 Exiting chatbot.")
            break
