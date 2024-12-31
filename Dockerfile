# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /vipv-server

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Ensure the instance folder exists
RUN mkdir -p /instance

# Expose the port the app runs on
EXPOSE 5000

# Define the command to run the application with gunicorn
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:5000", "flaskr:create_app()"]
