# Use Ubuntu as the base image
FROM ubuntu:22.04

# Set non-interactive mode for installations
ENV DEBIAN_FRONTEND=noninteractive

# Update and install dependencies
RUN apt-get update && apt-get install -y \
    wget\
    curl\
    nano\
    python3 python3-pip \
    qttools5-dev-tools \
    qtbase5-dev \
    qtchooser \
    qt5-qmake \
    qtbase5-dev-tools \
    x11-apps \
    libx11-6 \
    && rm -rf /var/lib/apt/lists/*

RUN wget -qO- https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list \
    && apt update && apt install -y google-chrome-stable

# Set working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy environment file into the container
COPY .env /app/.env

EXPOSE 8085

# Load environment variables
RUN echo "source /app/.env" >> ~/.bashrc

# Set entry point
CMD ["/bin/bash"]
