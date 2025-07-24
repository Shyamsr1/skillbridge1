FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install build dependencies for tokenizers & sentencepiece
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    curl \
    pkg-config \
    libssl-dev \
    rustc \
    && rm -rf /var/lib/apt/lists/*

# Copy all files to container
COPY . .

# Upgrade pip and install requirements
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the Streamlit port
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "skillbridge_dl_app.py", "--server.port=8501", "--server.enableCORS=false"]
