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
In the development environment:
1. Set a tag
	`TAG=0.0.1`
3. Build image (from Linux / WSL)
	From project root (where Dockerfile is)
	`docker build -t echedeyls/vipv-acquisition-server:$TAG .`
4. Push to DockerHub repository
	`docker push echedeyls/vipv-acquisition-server:$TAG`

In the production environment:
0. Set a tag
    `TAG=0.0.1`
1. Pull the image
    `docker pull echedeyls/vipv-acquisition-server:$TAG`
2. Clone the `docker-compose.yml` file from the repository:
    `wget https://raw.githubusercontent.com/isi-ies-group/VIPV-Data-Crowdsourcing-Server/refs/heads/main/docker-compose.yml`
3. Modify the `docker-compose.yml` file:
    - Change the `build: .` key to `image: echedeyls/vipv-acquisition-server:$TAG` to set the image to the one you just pulled. You can do this with the following command:
    `sed -i "s/build: .*/image: echedeyls\/vipv-acquisition-server:$TAG/" docker-compose.yml`
    - Change the environment variables to the ones you want to use.
4. Run the server
    `sudo docker compose -f docker-compose.yml up -d`

## Docker common commands
- List all containers
    `docker ps -a`
- Stop all containers
    `docker stop $(docker ps -a -q)`
- Remove all containers
    `docker rm $(docker ps -a -q)`
