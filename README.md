# Azure OpenAI Load Balancer App

A FastAPI application that provides load balancing across multiple Azure OpenAI instances.

## Features

- Load balancing across multiple Azure OpenAI endpoints
- Automatic failover on error responses
- Transparent proxy for all OpenAI API endpoints
- Request logging
- Docker container ready for Azure Container Apps

## Configuration

The application can be configured in several ways:

### 1. Environment Variables

- `OPENAI_INSTANCES`: A JSON string containing the OpenAI instances configuration
- `OPENAI_CONFIG_PATH`: Path to a JSON configuration file (default: `/config/openai_instances.json`)
- `LOG_LEVEL`: Logging level (default: INFO)
- `LOG_FILE`: Path to log file (optional)

### 2. Configuration File

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

## Running with Docker

### Running the Container

```bash
docker run -p 8000:80 \
  -v /path/to/your/config:/config \
  -v /path/to/logs:/app/logs \
  -e LOG_LEVEL=DEBUG \
  azure-openai-load-balancer
```

### Using Environment Variables for Configuration

```bash
docker run -p 8000:80 \
  -e OPENAI_INSTANCES='{"instances":[{"name":"instance1","url":"https://endpoint1.openai.azure.com","api_key":"key1"},{"name":"instance2","url":"https://endpoint2.openai.azure.com","api_key":"key2"}]}' \
  azure-openai-load-balancer
```

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