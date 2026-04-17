import json
import os
import subprocess
import threading
from asyncio import run
from time import sleep
from dotenv import dotenv_values
from BACKEND.Automation import Automation
from BACKEND.Model import FirstLayerDMW
from BACKEND.RealTimeSearchEngine import RealtimeSearchEngine
from BACKEND.SpeechToText import SpeechRecognition
from BACKEND.TextToSpeech import TextToSpeech
from FRONTEND.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToSpeech,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")

DefaultMessage = f'''{Username}: Hello {Assistantname}, How are you?
{Assistantname}: Welcome {Username}. I am doing well. How can I help you today?
'''

subprocesses = []
Funtions = ["open", "close", "play", "system", "google search", "youtube search"]

def ShowDefaultChatIfNoChats():
    
    with open(r'DATA\Chatlog.json', "r", encoding='utf-8') as file:
        if len(file.read()) < 5:
            with open(TempDirectoryPath('Database.data'), "w", encoding='utf-8') as f:
                f.write("")

def ReadChatlogJson():
    
    with open(r'DATA\Chatlog.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def ChatLogIntegration():
    
    json_data = ReadChatlogJson()
    formatted_chatlog = ""
    
    for entry in json_data:
        if entry["role"] == 'user':
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"

    formatted_chatlog = formatted_chatlog.replace("User", Username)
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname)

    with open(TempDirectoryPath('DataBase.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    
    with open(TempDirectoryPath('DataBase.data'), "r", encoding='utf-8') as file:
        data = file.read()
        if len(data) > 0:
            result = json.dumps(data.split('\n'), indent=2)
            with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as res_file:
                res_file.write(result)

def InitialExecution():
    
    SetMicrophoneStatus("False")
    ShowTextToSpeech(" ")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

def MainExecution():
    
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = " "

    SetAssistantStatus("Listening....")
    Query = SpeechRecognition()
    ShowTextToSpeech(f"{Username}: {Query}")
    SetAssistantStatus("Thinking...")
    
    Decision = FirstLayerDMW(Query)
    
    print("\nDecision:", Decision, "\n")

    G = any(i.startswith("general") for i in Decision)
    R = any(i.startswith("realtime") for i in Decision)

    Merged_query = json.dumps(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")],
        indent=2
    )

    for queries in Decision:
        
        if "generate " in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    for queries in Decision:
        
        if not TaskExecution:
            if any(queries.startswith(func) for func in Funtions):
                run(Automation(list(Decision)))
                TaskExecution = True

    if ImageExecution:
        
        with open(r"FRONTEND\FILES\ImageGeneration.data", "w") as file:
            file.write(f"{ImageGenerationQuery},True")
        try:
            p1 = subprocess.Popen(
                ['python', r'BACKEND\ImageGeneration.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False
            )
            subprocesses.append(p1)
        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")

    if G and R or R:
        
        SetAssistantStatus("Searching..")
        Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
        ShowTextToSpeech(f"{Assistantname}: {Answer}")
        SetAssistantStatus("Answering....")
        TextToSpeech(Answer)
        return True

    else:
        
        for Queries in Decision:
            if "general" in Queries:
                SetAssistantStatus("Thinking...")
                QueryFinal = Queries.replace("general ", "")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToSpeech(f"{Assistantname}: {Answer}")
                SetAssistantStatus("Answering....")
                TextToSpeech(Answer)
                return True

            elif "realtime" in Queries:
                SetAssistantStatus("Searching...")
                QueryFinal = Queries.replace("realtime ", "")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToSpeech(f"{Assistantname}: {Answer}")
                SetAssistantStatus("Answering....")
                TextToSpeech(Answer)
                return True

            elif "exit" in Queries:
                QueryFinal = "Okay, Bye Sir have a great day my master!!!"
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextToSpeech(f"{Assistantname}: {Answer}")
                SetAssistantStatus("Answering....")
                TextToSpeech(Answer)
                SetAssistantStatus(Answer)
                os._exit(1)

def FirstThread():
    
    while True:
        CurrentStatus = GetMicrophoneStatus()
        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available..." in AIStatus:
                sleep(0.1)
            else:
                SetAssistantStatus("Available...")

def SecondThread():
    
    GraphicalUserInterface()

if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()
