# Using develop branch for register json schema function
FROM ghcr.io/sage-bionetworks/synapsepythonclient:develop-184718b7262d20d6742f1ffe86fb86a94cc48fae

# Copy requirements and install dependencies
RUN pip install --no-cache-dir synapseclient[curator]

# Copy Python script
COPY src/register_json_schemas.py /usr/local/bin/register_json_schemas.py

# Set working directory to GitHub workspace
WORKDIR /github/workspace

# Set entrypoint to Python script
ENTRYPOINT ["python", "/usr/local/bin/register_json_schemas.py"]
