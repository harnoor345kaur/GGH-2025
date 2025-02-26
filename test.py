import google.generativeai as genai

genai.configure(api_key="your-api-key-here")

# Fetch and print available models
models = list(genai.list_models())  # Convert generator to a list
for model in models:
    print(model.name)  # Print model names

