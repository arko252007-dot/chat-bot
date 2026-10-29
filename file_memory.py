import os
from datetime import date
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_FILE = os.path.join(SCRIPT_DIR, "memory.txt")

while True:
    prompt = input("Enter your prompt: ")

    memory_context = ""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            memory_context = f.read()

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Known user info:\n{memory_context}\n\nUser says: {prompt}"
    )
    print("Response:", response.text)

    extract_prompt = f"""You are a memory extraction assistant. Analyze the user message below and determine if it contains long-term personal facts or preferences worth remembering for future conversations.

Current Date: {date.today()}
User message: "{prompt}"

Guidelines:
- What to SAVE: Personal identity, preferences, habits, relationships, background, or enduring constraints (e.g., name, location, likes/dislikes, hobbies, job, dietary needs).
- What to IGNORE: Greetings, casual banter, general questions, transient tasks, temporary states (e.g., "I'm busy right now"), or prompts asking the bot to perform an action.

Output Rules:
1. If there is a personal detail to remember, summarize it into a concise third-person statement starting with "{date.today()}: ".
2. Return ONLY the fact itself—no quotes, labels, or explanatory text.
3. If there is nothing long-term to save, return ONLY: NONE

Examples:
- "My name is Krish" -> {date.today()}: User's name is Krish
- "My favorite color is red" -> {date.today()}: User loves the color red
- "I work as a software engineer in Berlin" -> {date.today()}: User works as a software engineer in Berlin
- "Hello, how are you?" -> NONE
- "Can you explain quantum computing?" -> NONE
- "I'm feeling a bit tired today" -> NONE"""

    fact = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=extract_prompt
    ).text.strip()

    if fact and "NONE" not in fact:
        with open(MEMORY_FILE, "a") as f:
            f.write(fact + "\n")
        # print(f"-> Saved to {MEMORY_FILE}: {fact}\n")

