from fastapi.testclient import TestClient
from src.main import app
from unittest.mock import patch
import json

client = TestClient(app)

def test_load_balancer_success():
    with patch('src.services.openai_service.OpenAIService.forward_request') as mock_forward:
        mock_forward.return_value = {"result": "success"}
        response = client.post("/api/forward", json={"data": "test"})
        assert response.status_code == 200
        assert response.json() == {"result": "success"}

def test_load_balancer_failure_switch():
    with patch('src.services.openai_service.OpenAIService.forward_request') as mock_forward:
        mock_forward.side_effect = [{"error": "failed"}, {"result": "success"}]
        response = client.post("/api/forward", json={"data": "test"})
        assert response.status_code == 200
        assert response.json() == {"result": "success"}

def test_load_balancer_all_failures():
    with patch('src.services.openai_service.OpenAIService.forward_request') as mock_forward:
        mock_forward.return_value = {"error": "failed"}
        response = client.post("/api/forward", json={"data": "test"})
        assert response.status_code == 502
        assert response.json() == {"error": "All instances failed."}

def test_load_balancer_non_200_response():
    with patch('src.services.openai_service.OpenAIService.forward_request') as mock_forward:
        mock_forward.return_value = {"error": "not found"}
        response = client.post("/api/forward", json={"data": "test"})
        assert response.status_code == 502
        assert response.json() == {"error": "All instances failed."}