FROM python:3.8-slim

# Install required build tools and libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    gfortran \
    libatlas-base-dev \
    liblapack-dev \
    libblas-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to ensure we get pre-built wheels where possible
# RUN pip install --upgrade pip

# Copy application files and install Python dependencies
COPY . /app
WORKDIR /app 
RUN pip install -r requirements.txt

# Creating environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose the port
EXPOSE 5000

# Run the application
CMD ["flask", "run"]





