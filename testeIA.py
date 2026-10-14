from ollama import Client

# IP do Celular onde o servidor Ollama está rodando
OLLAMA_HOST = "http://192.168.51.10:11434"
client = Client(host=OLLAMA_HOST)
prompt = 'Olá, teste de conexão!'

resposta = client.chat(
    model='qwen2.5:1.5b',
    messages=[{'role': 'user', 'content': prompt}]
)

print(resposta['message']['content'])