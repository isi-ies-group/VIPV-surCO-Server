# Use the official Python image from the Docker Hub
FROM python:3.12-alpine

# As Root
# Copy the requirements file into the container
COPY requirements.txt .

# As Root
# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create the user and group to run the application
RUN addgroup -S vipv-server && adduser -S vipv-server -G vipv-server

# Create the directory and set the ownership to the user
RUN mkdir /vipv-server && chown vipv-server:vipv-server /vipv-server

# Switch to the user
USER vipv-server

# Set the working directory in the container
WORKDIR /vipv-server

# Copy the rest of the application code into the container
COPY . .

# Ensure the instance folder exists
RUN mkdir -p instance

# Expose the port the app runs on
EXPOSE 5000

# Define the command to run the application with gunicorn
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:5000", "flaskr:create_app()"]
