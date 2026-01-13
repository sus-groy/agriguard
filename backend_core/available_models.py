from google import genai

client = genai.Client(api_key="AIzaSyAWaBnNsoYbRFbI87OPPpnEQcUgNkzaRjg")
print("Available models that support generate_content:\n")

for model in client.models.list():
    # Show name and display name
    print(f"- {model.name} (display: {getattr(model, 'display_name', 'unknown')})")

    # Try both fields for supported methods
    supported = []
    if hasattr(model, "supported_generation_methods"):
        supported = model.supported_generation_methods
    elif hasattr(model, "supported_actions"):
        supported = model.supported_actions

    # Print supported methods
    print(f"    methods: {supported}")

    if "generateContent" in supported:
        print("    → supports generateContent!")