# Instructions to setup the server
## Overview
This server is intended to be deployed in a remote server, and it is designed to be run with Docker and Docker Compose.

The server is composed of two services:
- `web`: The Flask server that serves the API.
- `db`: The PostgreSQL database.

The server uses a volume to store the database used by the `db` service.

Another volume (bind mount) is used to store the data sessions of the Flask server.

Note that from the start, the server counts with an admin user different from `sudo`.

The admin user requires being in the `docker` group to run Docker commands.

Another user, `vipv-user`, is created to own the volume where the data sessions are stored. This user has UID 5001 and GID 5001, to match the Dockerfile. It also belongs to the `docker` group.

## One-time set up of the remote server
1. Install Docker and Docker Compose
    ```bash
    sudo apt-get update
    sudo apt-get install docker.io
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo apt-get install docker-compose
    ```
2. Add the current (admin) user to the `docker` group
    ```bash
    sudo usermod -aG docker $USER
    ```
3. Log out and log back in
4. Create a user for the server volume with UID 5001 and GID 5001 (to match Dockerfile).
    This is to avoid permission issues with the volume, as the `web` container user `vipv-user` has UID 5001 and GID 5001, and it will try to write to the volume.

    Then, assign the volume ownership to the user:
    ```bash
    # create user and group
    sudo addgroup --gid 5001 vipv-group
    sudo adduser --uid 5001 --ingroup vipv-group vipv-user
    sudo passwd -d vipv-user
    # add user to docker group
    sudo usermod -aG docker vipv-user
    # create volume and assign ownership
    sudo mkdir --parents /home/vipv-user/sessions
    sudo chown -R vipv-user:vipv-group /home/vipv-user/sessions
    ```

### Nginx configuration file for the surCO server (web + api)

At `/etc/nginx/sites-available/surCO_app`, view file `surCO_app`
And create a simlink `ln -s ../sites-available/surCO_app .` from `/etc/nginx/sites-enabled`

## Deployment (if `docker-compose.yml` was modified)
In the production environment:

1. Log in to the user that will run the server
    `su --login vipv-user`
2. Pull the image
    `docker pull echedeyls/vipv-acquisition-server:latest`
3. Clone the `docker-compose.yml` file from the repository:
    `cd ~ && wget https://raw.githubusercontent.com/isi-ies-group/VIPV-surCO-Server/refs/heads/main/docker-compose.yml -O docker-compose.yml`
4. Modify the `docker-compose.yml` file:
    - Change the `build: .` key to `image: echedeyls/vipv-acquisition-server:latest` to set the image to the one you just pulled. You can do this with the following command:
    `sed -i "s/build: .*/image: echedeyls\/vipv-acquisition-server:latest/" docker-compose.yml`
    - Change the environment variables to the ones you want to use.
5. Run the server
    `docker compose -f docker-compose.yml up -d`

## Updating the web server (assuming the `docker-compose.yml` file was not modified)
```bash
su --login vipv-user
# Pull the image
docker pull echedeyls/vipv-acquisition-server:latest
# Restart the server with the new image
docker compose -f docker-compose.yml up -d
```

## Docker common commands
- List all containers
    `docker ps -a`
- Stop all containers
    `docker stop $(docker ps -a -q)`
- Remove all containers
    `docker rm $(docker ps -a -q)`
- Remove all dangling volumes
    `docker volume rm $(docker volume ls -qf dangling=true)`
- Remove all images
    `docker rmi $(docker images -q)`


## Direct database manipulation

This is a walkthrough of how to manage the database of the server.

1. Login as the user that manages the server
    `su --login vipv-user`
2. Review the contents of `docker-compose.yml` to confirm the configuration
    `cat docker-compose.yml`
3. Use `docker exec` to open a terminal in the db container:
    `docker exec -it db bash`
    If this command fails, you may need to check the status of the containers
    and their names with `docker ps -a`. `db` is the default name of the container
    in the `docker exec -it <name> <command>` command.
4. Access the database
    `psql -U db_user -d vipv_db`
5. Verifying Database Schema and Tables:

    1. List all available databases:
        `\l`

    2. Switch to the target database:
        `\c vipv_db`

    3. View all tables in the schema:
        `\dt`

### Example: get the user for a given ID

```sql
SELECT id, username, email FROM "UserCredentials" WHERE id = 1;
```
