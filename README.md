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


## Using in Azure Container Apps
Enter the container application creation through Azure Portal

![image](https://github.com/user-attachments/assets/dc9fcd27-48c6-4c69-8bbd-54f81cb603bf)


Configure the container image for implementing load balancing and fill it in: sulitu/azure-openai-load-balancer-app:v1.3

![image](https://github.com/user-attachments/assets/81356f43-8f5c-4814-a24a-d3beb09b8e71)


Configure the network rules and set the port to 8000

![image](https://github.com/user-attachments/assets/2fd5314a-aeba-4247-b083-d3e86017553c)

Click "Create Container Application Instance"



### Environment Variables

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


- `API_KEY`: Your custom API key for accessing the Azure Container App.
************

### Configure the container application environment variables

![image](https://github.com/user-attachments/assets/46e25eaf-92a9-45df-bbde-3b58d672ba67)


![image](https://github.com/user-attachments/assets/80789428-4fd4-4675-accb-2ee90f5d9b17)

Click Save - Create


## Send a test request

View the ACA container application overview to obtain the Endpoint address of ACA.

![image](https://github.com/user-attachments/assets/02ed2b4f-95bb-4ba8-852f-36e8bfdbc53f)


Test request command
```bash
curl -X POST "$API_ENDPOINT/openai/deployments/gpt-4o/chat/completions?api-version=2025-01-01-preview" \
  -H "Content-Type: application/json" \
  -H 'Authorization: Bearer $API_KEY' \
  -d '{
          "model": "gpt-4o",
          "messages": [
            {
              "role": "user",
              "content": [
                {
                  "type": "text",
                  "text": "hi"
                }
              ]
            }
          ],
          "max_tokens": 300
        }'
```

### Parameter Description

- `$API_ENDPOINT` in the `curl` request refers to the **access URL of the Container App** copied in the previous step.
- `$API_KEY` in the request header is your **custom API key for the Container App**.


## Others

### Configuration requirements
To create an instance in Azure OpenAI, the instance name and the deployment name need to be consistent

![image](https://github.com/user-attachments/assets/b4af6cb2-01c5-4e2f-9b4d-db56bcba486a)


### Request format
Only the domain name of the requested api needs to be replaced. The references for other path parameters and query parameters are the same as those for Azure OpenAI.
The request body can be requested in the format required by each model of Azure OpenAI.

###  Expenses
In addition to the token fees consumed by Azure OpenAI at the back end, there will also be ACA fees for container applications. For reference:
https://learn.microsoft.com/zh-cn/azure/container-apps/billing#consumption-dedicated
