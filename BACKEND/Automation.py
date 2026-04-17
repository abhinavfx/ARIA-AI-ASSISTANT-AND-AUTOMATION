from AppOpener import close, open as appopen 
from webbrowser import open as webopen
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from bs4 import BeautifulSoup
from rich import print
from groq import Groq 
import webbrowser
import subprocess
import requests
import keyboard
import asyncio 
import os

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")

useragent = 'Mozilla/50 (Windows NT 11.0; Win64; x64) Applewebkit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

client = Groq(api_key=GroqAPIKey)

# ✅ Open App Function (Fallback to Web Search)
def OpenApp(app, sess=requests.session()):
    try:
        app = app.lower().strip()
        appopen(app, match_closest=True, throw_error=True)
        return True
    except Exception:
        print(f"App '{app}' not found, trying web search...")
        
        url = f"https://www.google.com/search?q={app}+download"
        webopen(url)
        return True

# ✅ Close App Function
def CloseApp(app):
    try:
        close(app, match_closest=True, output=True, throw_error=True)
        return True
    except:
        return False

# ✅ Search on Google
def GoogleSearch(topic):
    search(topic)
    return True

# ✅ Play on YouTube
def PlayYouTube(query):
    playonyt(query)
    return True

# ✅ System Commands (Volume, Mute, Unmute)
def System(command):
    actions = {
        "mute": lambda: keyboard.press_and_release("volume mute"),
        "unmute": lambda: keyboard.press_and_release("volume unmute"),
        "volume up": lambda: keyboard.press_and_release("volume up"),
        "volume down": lambda: keyboard.press_and_release("volume down"),
    }
    action = actions.get(command.lower())
    if action:
        action()
        return True
    return False

# ✅ AI Content Generator
def Content(topic):
    topic = topic.lower().replace("content ", "").strip()

    def OpenNotepad(file):
        subprocess.Popen(["notepad.exe", file])

    def ConentWriterAI(prompt):
        messages = [{"role": "user", "content": prompt}]
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=10000,
            temperature=0.7,
        )
        return completion.choices[0].message.content

    content_by_ai = ConentWriterAI(topic)
    
    file_path = rf"Data\{topic.replace(' ', '_')}.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content_by_ai)
    
    OpenNotepad(file_path)
    return True

# ✅ Command Processor
async def TranslateAndExecute(commands):
    tasks = []
    
    for command in commands:
        command_lower = command.lower().strip()

        if command_lower.startswith("open "):
            app_name = command_lower.replace("open ", "", 1).strip()
            tasks.append(asyncio.to_thread(OpenApp, app_name))
        
        elif command_lower.startswith("close "):
            app_name = command_lower.replace("close ", "", 1).strip()
            tasks.append(asyncio.to_thread(CloseApp, app_name))
        
        elif command_lower.startswith("play "):
            query = command_lower.replace("play ", "", 1).strip()
            tasks.append(asyncio.to_thread(PlayYouTube, query))
        
        elif command_lower.startswith("content "):
            topic = command_lower.replace("content ", "", 1).strip()
            tasks.append(asyncio.to_thread(Content, topic))
        
        elif command_lower.startswith("google search "):
            topic = command_lower.replace("google search ", "", 1).strip()
            tasks.append(asyncio.to_thread(GoogleSearch, topic))
        
        elif command_lower.startswith("system "):
            action = command_lower.replace("system ", "", 1).strip()
            tasks.append(asyncio.to_thread(System, action))
        
        else:
            print(f"No function found for: {command}")

    results = await asyncio.gather(*tasks)
    return results

# ✅ Automation Function
async def Automation(commands):
    return await TranslateAndExecute(commands)

# ✅ Run Main Function
if __name__ == "__main__":
    commands_list = [
        "open facebook",
        "close instagram",
        "close telegram",
        "close discord",
        "play attention charlie",
        "content application for 3 days leave",
    ]
    asyncio.run(Automation(commands_list))
