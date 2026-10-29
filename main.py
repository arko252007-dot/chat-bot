import os
from dotenv import load_dotenv
from mem0 import MemoryClient
from google import genai

load_dotenv()

mem0_client = MemoryClient(api_key=os.getenv("MEM0_API_KEY"))
gemini_client = genai.Client()

while True:
    prompt = input("Enter your prompt: ")
    if not prompt.strip():
        continue
    if prompt.lower() in ("exit", "quit"):
        break

    try:
        search_results = mem0_client.search(
            query=prompt,
            filters={"user_id": "krish"}
        )
        items = search_results.get("results", []) if isinstance(search_results, dict) else search_results
        memories = [item["memory"] for item in items if isinstance(item, dict) and "memory" in item]
    except Exception as e:
        print(f"[Warning] Failed to fetch memories: {e}")
        memories = []

    memory_context = "\n".join(f"- {m}" for m in memories) if memories else "No relevant memories found."

    full_prompt = f"""Context from user memory:
{memory_context}

User says: {prompt}"""

    try:
        response = gemini_client.models.generate_content(
            model="gemini-3.5-flash",
            contents=full_prompt
        )
        print("Response:", response.text)

        mem0_client.add(
            messages=[
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": response.text}
            ],
            user_id="krish"
        )
    except Exception as e:
        print(f"Error during response generation/saving: {e}")
