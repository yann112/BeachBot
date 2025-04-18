import pytest
from dotenv import load_dotenv
from beachbot.llm import OpenRouterClient

# Load environment variables from the .env file
load_dotenv()

@pytest.mark.integration
def test_api_integration():
    client = OpenRouterClient()
    
    prompt = "it is for testing purpose just answer the single word 'ready' nothing more"
    result = client(prompt)
    
    assert result is not None, "The API did not return a response."
    
    assert "ready" in result.lower(), f"Unexpected response: {result}"