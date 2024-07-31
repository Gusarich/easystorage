# Use the official Ubuntu 20.04 as a base image
FROM ubuntu:20.04

# Set the environment variable to noninteractive mode
ENV DEBIAN_FRONTEND=noninteractive

# Install wget
RUN apt-get update && \
    apt-get install -y wget curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Download the tonutils-storage binary
RUN wget -O /usr/local/bin/tonutils-storage-linux-amd64 https://github.com/xssnick/tonutils-storage/releases/download/v0.6.5/tonutils-storage-linux-amd64 && \
    chmod +x /usr/local/bin/tonutils-storage-linux-amd64

# Create the storage directory
RUN mkdir -p /tonutils-storage-db

# Expose the ports
EXPOSE 8080 17555/udp

# Start the tonutils-storage binary with specified options
CMD ["/usr/local/bin/tonutils-storage-linux-amd64", "--daemon", "--api", "0.0.0.0:8080"]
