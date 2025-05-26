# Azure OpenAI Load Balancer App

A FastAPI application that provides load balancing across multiple Azure OpenAI instances.


## Features

- Load balancing across multiple Azure OpenAI endpoints
- Automatic failover on error responses
- Transparent proxy for all OpenAI API endpoints
- Request logging
- Docker container ready for Azure Container Apps


## API Usage

Use the application exactly as you would use the Azure OpenAI API. All requests are transparently forwarded to the backend instances with load balancing.


## Architecture

![image](https://github.com/user-attachments/assets/2523aa7a-6179-48b2-8c9c-654566b27678)


## Deployment steps

## Using in Azure Container Apps
Enter the container application creation through Azure Portal
![image](https://github.com/user-attachments/assets/dc9fcd27-48c6-4c69-8bbd-54f81cb603bf)

Configure the container image for implementing load balancing and fill it in: duojie/azure-openai-load-balancer-app:v1.3
![image](https://github.com/user-attachments/assets/81356f43-8f5c-4814-a24a-d3beb09b8e71)

Configure the network rules and set the port to 8000
![image](https://github.com/user-attachments/assets/2fd5314a-aeba-4247-b083-d3e86017553c)

Click "Create Container Application Instance"




## Environment Variables

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

