from google import genai

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key="AIzaSyCv-kGbHn7qLTIlnceJJgU0ykuA8R9or7o")

response = client.models.generate_content(
    model="gemini-2.5-flash", contents="Explain briefly and with simple vocabulary how Capital One can help users grow their savings"
)
print(response.text)

with open("forecast/response.txt", "w") as f:
    f.write(response)