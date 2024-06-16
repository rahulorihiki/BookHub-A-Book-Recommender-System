# Use an official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app
RUN pip install -r requirements.txt

# Make port 7000 available to the world outside this container
EXPOSE 7000

# Run app.py when the container launches
CMD ["python", "api_call.py"]
