from llama_cpp import Llama

# 🔹 Load model
llm = Llama(model_path="bigdata/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf", n_ctx=4096, n_threads=8)
print("✅ Model loaded. Start chatting! (Type 'exit' to quit)\n")

# 🔹 Chat loop
history = ""
while True:
    user_input = input("🧑 You: ")
    if user_input.lower() in ["exit", "quit"]:
        break

    history += f"\nUser: {user_input}\nAssistant:"
    output = llm(history, max_tokens=400, temperature=0.7, top_p=0.9)
    answer = output["choices"][0]["text"].strip()
    print(f"🤖 Assistant: {answer}\n")
    history += f" {answer}"

