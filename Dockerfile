# Use an official Python runtime as the base image
FROM python:3.12-slim

# Set working directory in the container
WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire src directory
COPY src/ ./src
COPY data/ ./data

# Expose the port Streamlit uses
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "src/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]