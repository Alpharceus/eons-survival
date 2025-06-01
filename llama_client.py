import requests

OLLAMA_URL = 'http://localhost:11434/api/generate'
MODEL = 'llama3'

def stream_llm(prompt):
    payload = {
        'model': MODEL,
        'prompt': prompt,
        'stream': True
    }
    with requests.post(OLLAMA_URL, json=payload, stream=True) as r:
        for line in r.iter_lines():
            if line:
                chunk = line.decode('utf-8')
                if '"response":' in chunk:
                    # Naive extraction: you can improve this as needed
                    text = chunk.split('"response":',1)[1].split(',"',1)[0]
                    yield text.strip(' "')
