# Azure OpenAI Load Balancer App

A FastAPI application that provides load balancing across multiple Azure OpenAI instances.

## Features

- Load balancing across multiple Azure OpenAI endpoints
- Automatic failover on error responses
- Transparent proxy for all OpenAI API endpoints
- Request logging
- Docker container ready for Azure Container Apps


## Architecture
![image](https://github.com/user-attachments/assets/2523aa7a-6179-48b2-8c9c-654566b27678)

## Deployment steps


## Using in Azure Container Apps

1. Build and push the container to your registry
2. Create an Azure Container App
3. Configure the container app with either:
   - Mount a persistent volume for `/config`
   - Set the `OPENAI_INSTANCES` environment variable with your configuration

## API Usage

Use the application exactly as you would use the Azure OpenAI API. All requests are transparently forwarded to the backend instances with load balancing.

## Deployment with Docker Compose

### Quick Start

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/azure-openai-load-balancer-app.git
   cd azure-openai-load-balancer-app
   ```

### 1. Environment Variables

- `OPENAI_INSTANCES`: A JSON string containing the OpenAI instances configuration

Create a JSON file with the following structure:

```json
{
  "instances": [
    {
      "name": "instance1",
      "url": "https://your-endpoint.openai.azure.com",
      "api_key": "your-api-key"
    },
    {
      "name": "instance2",
      "url": "https://your-second-endpoint.openai.azure.com",
      "api_key": "your-second-api-key"
    }
  ]
}
```

