FROM solidnerd/bookstack:25.2.1

# Switch to root so we can install things
USER root

# Install packages / patch tools
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        patch \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Switch back to the container's default user
USER www-data