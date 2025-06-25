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

![image](https://github.com/user-attachments/assets/15d3843f-7606-402d-a41b-92d24ceb7ffc)



Configure the container image for implementing load balancing and fill it in: sulitu/azure-openai-load-balancer-app:v1.3

![image](https://github.com/user-attachments/assets/26f30329-3e64-4287-b815-08f0301d2058)



Configure the network rules and set the port to 8000

![image](https://github.com/user-attachments/assets/abcf6b74-05df-4d5f-a2cc-e8e19b2393c0)


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

![image](https://github.com/user-attachments/assets/e3c92eb8-2804-4b83-bcef-c2baf066fd4c)



![image](https://github.com/user-attachments/assets/d0c0e2e0-b577-4b0f-a62f-db567e340c7c)


Click Save - Create


## Send a test request

View the ACA container application overview to obtain the Endpoint address of ACA.

![image](https://github.com/user-attachments/assets/18133562-b875-4289-b63e-0e2e6ced6433)



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

![image](https://github.com/user-attachments/assets/738adac1-54d8-4672-ab1b-46c4163d3051)


### Request format
Only the domain name of the requested api needs to be replaced. The references for other path parameters and query parameters are the same as those for Azure OpenAI.
The request body can be requested in the format required by each model of Azure OpenAI.

###  Expenses
In addition to the token fees consumed by Azure OpenAI at the back end, there will also be ACA fees for container applications. For reference:
https://learn.microsoft.com/zh-cn/azure/container-apps/billing#consumption-dedicated
