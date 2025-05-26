def setup_logging():
    import logging
    import os

    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, 'app.log')),
            logging.StreamHandler()
        ]
    )

def log_request(request):
    logging.info(f"Request: {request.method} {request.url} - Body: {request.body()}")

def log_response(response):
    logging.info(f"Response: {response.status_code} - Body: {response.body}")