from transformers import pipeline

def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

# Local model (no API)
model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
llm = pipeline("text-generation", model=model_name)

def local_agent(prompt):
    if "weather" in prompt.lower():
        import re
        m = re.search(r"in\s+([A-Za-z ]+)", prompt)
        if m:
            city = m.group(1).strip()
            return get_weather(city)
    return llm(prompt, max_new_tokens=100)[0]["generated_text"]

print(local_agent("what is the weather in San Francisco?"))

