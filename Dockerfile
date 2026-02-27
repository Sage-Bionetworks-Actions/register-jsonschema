# Using develop branch for register json schema function
FROM ghcr.io/sage-bionetworks/synapsepythonclient:develop-486a9fc457d4fae8b54c9823fc195c3b38ae3eb9

# Copy requirements and install dependencies
RUN pip install --no-cache-dir synapseclient[curator]

# Copy Python script
COPY src/register_json_schemas.py /usr/local/bin/register_json_schemas.py

# Set working directory to GitHub workspace
WORKDIR /github/workspace

# Set entrypoint to Python script
ENTRYPOINT ["python", "/usr/local/bin/register_json_schemas.py"]
