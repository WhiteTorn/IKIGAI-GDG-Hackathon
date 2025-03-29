# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
# Define PORT for Cloud Run compatibility
ENV PORT 8080
# Set PYTHONUNBUFFERED to ensure logs are sent correctly
ENV PYTHONUNBUFFERED True

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend application code into the container at /app
COPY . .

# Make port 8080 available to the world outside this container
EXPOSE $PORT

# Define environment variable for Flask app (optional, can be set in Cloud Run)
# ENV FLASK_APP=app.py

# Run app.py when the container launches using Flask's built-in server
# Use 0.0.0.0 to ensure it's accessible from outside the container
# Use $PORT environment variable for Cloud Run compatibility
CMD ["flask", "run", "--host=0.0.0.0", "--port=$PORT"]

# Alternative using gunicorn (often preferred for production, but flask run is simpler for MVP)
# CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:app"]
# If using gunicorn, add it to requirements.txt