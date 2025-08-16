
# Use a lightweight Python base image
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies (needed for numpy, pandas, matplotlib, lxml, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ \
    libssl-dev libffi-dev \
    libxml2-dev libxslt1-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*


# Copy requirements file and install dependencies
COPY requirements.txt .

# Then install packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your project files
COPY . .

# Copy .env file
COPY .env ./
# Expose Streamlit default port
EXPOSE 8501

# Run your Streamlit app by default
CMD ["streamlit", "run", "Main_mod.py", "--server.port=8501", "--server.address=0.0.0.0"]
