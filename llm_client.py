import os
import json
import logging
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GSTAuditEngine-LLM")

class LLMClient:
    """
    Dual-Provider LLM Engine supporting AWS Bedrock (Primary Cloud) 
    with automatic fallback to local Ollama.
    """
    def __init__(self, provider: str = "bedrock", region: str = "us-east-1"):
        self.provider = os.getenv("LLM_PROVIDER", provider).lower()
        self.region = os.getenv("AWS_REGION", region)
        self.bedrock_model_id = os.getenv("BEDROCK_MODEL_ID", "meta.llama3-1-8b-instruct-v1:0")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1")

    def query(self, prompt: str) -> str:
        if self.provider == "bedrock":
            try:
                return self._call_bedrock(prompt)
            except Exception as e:
                logger.warning(f"AWS Bedrock execution failed: {e}. Falling back to local Ollama...")
                return self._call_ollama(prompt)
        else:
            return self._call_ollama(prompt)

    def _call_bedrock(self, prompt: str) -> str:
        import boto3
        
        client = boto3.client(
            service_name="bedrock-runtime",
            region_name=self.region
        )
        
        # Payload structure for Meta Llama on Bedrock
        payload = {
            "prompt": f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>",
            "max_gen_len": 512,
            "temperature": 0.1,
            "top_p": 0.9
        }
        
        response = client.invoke_model(
            modelId=self.bedrock_model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(payload)
        )
        
        response_body = json.loads(response.get("body").read())
        return response_body.get("generation", "").strip()

    def _call_ollama(self, prompt: str) -> str:
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(self.ollama_url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json().get("response", "").strip()

def get_llm_response(prompt: str) -> str:
    client = LLMClient()
    return client.query(prompt)
