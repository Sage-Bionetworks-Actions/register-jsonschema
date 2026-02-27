# Using develop branch for register json schema function
FROM ghcr.io/sage-bionetworks/synapsepythonclient:develop-5ca3142c4a42a70a22302b722b1a26582bc306aa

# Copy requirements and install dependencies
RUN pip install --no-cache-dir synapseclient[curator]

# Copy Python script
COPY src/register_json_schemas.py /usr/local/bin/register_json_schemas.py

# Set working directory to GitHub workspace
WORKDIR /github/workspace

# Set entrypoint to Python script
ENTRYPOINT ["python", "/usr/local/bin/register_json_schemas.py"]
