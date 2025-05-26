from fastapi import HTTPException
import requests
import json
import random
from typing import List, Dict

class LoadBalancer:
    def __init__(self, instances: List[str]):
        self.instances = instances
        self.current_instance_index = 0

    def get_next_instance(self) -> str:
        instance = self.instances[self.current_instance_index]
        self.current_instance_index = (self.current_instance_index + 1) % len(self.instances)
        return instance

    def forward_request(self, endpoint: str, payload: Dict) -> Dict:
        for _ in range(len(self.instances)):
            instance = self.get_next_instance()
            try:
                response = requests.post(f"{instance}/{endpoint}", json=payload)
                if response.status_code == 200:
                    return response.json()
                else:
                    continue  # Try the next instance if the response is not 200
            except requests.RequestException:
                continue  # Try the next instance on exception
        raise HTTPException(status_code=503, detail="All instances are unavailable")