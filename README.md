# VIPV Data Crowdsourcing Server

Server for a community-sourced photovoltaic data collection project.

## Installation for development

1. Install Python dependencies from `requirements.txt` and `requirements-dev.txt`:
    ```bash
    python -m pip install -r requirements.txt
    python -m pip install -r requirements-dev.txt
    ```
    Other Python versions may work too.
2. For development, you may not need to set environment variables, but keep in mind they are heavily used in the Docker configuration for local testing and deployment.
3. Run the server for debugging:
    ```bash
    python -m flask --app flaskr run --host=0.0.0.0 --debug
    ```

## Docker development
- Build and deploy the server:
    `docker compose up --build`

## Deployment
In the development environment, at project root (where Dockerfile is):

1. Build image (from Linux / WSL)
	`docker build -t echedeyls/vipv-acquisition-server:latest .`
2. Push to DockerHub repository
	`docker push echedeyls/vipv-acquisition-server:latest`

Shortcut to run both commands:

```bash
docker build -t echedeyls/vipv-acquisition-server:latest . && docker push echedeyls/vipv-acquisition-server:latest
```

Follow the instructions in the `README_SERVER.md` file to deploy the server in a remote server.
