# Use the official Python image from the Docker Hub
FROM python:3.13-alpine

# As Root from the start
# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create the user and group to run the application
RUN addgroup --system vipv-group --gid 5001
RUN adduser --system vipv-user --ingroup vipv-group --uid 5001

# Create the directory and set the ownership to the user
RUN mkdir --parents /vipv-server
RUN chown vipv-user:vipv-group /vipv-server

# Switch to the user
USER vipv-user

# Set the working directory in the container
WORKDIR /vipv-server

# Copy the rest of the application code into the container
COPY . .

# Ensure the instance/sessions folder exists
RUN mkdir --parents instance/sessions

# Set permissions so the user can write and create subdirectories
RUN chmod 744 instance

# Define the volume
VOLUME ["/vipv-server/instance/sessions"]

# Expose the port the app runs on to the outside world
EXPOSE 5000

# Define the command to run the application with gunicorn
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:5000", "flaskr:create_app()"]
