"""
Register JSON schemas to Synapse organization.

This script registers JSON schemas from a directory to a Synapse organization.
The semantic version is passed as a parameter, NOT included in the schema name.
"""

import os
import json
import re
import sys
from pathlib import Path

from synapseclient import Synapse
from synapseclient.models import JSONSchema, SchemaOrganization


def main() -> 1 | 0:
    """
    Main function to generate JSON schemas from data models.
    Expects the following environment variables:
    - VERSION: Semantic version (e.g., '1.0.0')
    - ORG_NAME: Organization name
    - SCHEMA_DIR: Directory containing JSON schemas
    """
    version = os.environ.get("VERSION")
    org_name = os.environ.get("ORG_NAME")
    schema_dir = os.environ.get("SCHEMA_DIR")

    if not version:
        print("::error:: VERSION environment variable is required", file=sys.stderr)
        return 1

    if not org_name:
        print("::error:: ORG_NAME environment variable is required", file=sys.stderr)
        return 1

    if not schema_dir:
        print("::error:: SCHEMA_DIR environment variable is required", file=sys.stderr)
        return 1

    return register_schemas_from_directory(
        org_name=org_name,
        schema_dir=schema_dir,
        version=version,
    )


def register_schemas_from_directory(
    org_name: str,
    schema_dir: str,
    version: str,
) -> 1 | 0:
    """
    Register all JSON schemas from a directory.

    Args:
        org_name: Organization name
        schema_dir: Directory containing JSON schemas
        version: Semantic version (e.g., '1.0.0')
    """
    syn = Synapse()
    syn.login()

    print(f"\n{'='*60}")
    print("JSON Schema Registration")
    print(f"{'='*60}")
    print(f"Organization: {org_name}")
    print(f"Version: {version}")
    print(f"Schema Directory: {schema_dir}")
    print(f"{'='*60}\n")

    if version.startswith('v'):
        version = version[1:]

    try:
        org = SchemaOrganization(name=org_name)
        org.get(synapse_client=syn)
        print(f"✓ Organization found: {org_name}\n")
    except Exception as e:
        print(f"::error:: Organization not found: {org_name}", file=sys.stderr)
        print(f"::error:: {str(e)}", file=sys.stderr)
        return 1

    schema_dir = Path(schema_dir)
    if not schema_dir.exists():
        print(f"::error:: Schema directory not found: {schema_dir}", file=sys.stderr)
        return 1

    json_files = list(schema_dir.glob("*.json"))
    if not json_files:
        print(f"::error:: No JSON files found in: {schema_dir}", file=sys.stderr)
        return 1

    print(f"Found {len(json_files)} JSON schema file(s)\n")

    success_count = 0
    failed_count = 0

    for json_file in sorted(json_files):
        result = register_schema(syn, json_file, org_name, version)
        if result:
            success_count += 1
        else:
            failed_count += 1

    print(f"{'='*60}")
    print("Registration Summary")
    print(f"{'='*60}")
    print(f"Total Processed: {len(json_files)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {failed_count}")
    print(f"{'='*60}")

    if failed_count > 0:
        return 1
    return 0


def register_schema(
    syn: Synapse, json_file: Path, org_name: str, version: str
) -> JSONSchema | None:
    """
    Register a single JSON schema to Synapse.

    Args:
        syn: Synapse client
        json_file: Path to JSON schema file
        org_name: Organization name
        version: Semantic version (e.g., '1.0.0')

    Returns:
        JSONSchema object if successful, None otherwise
    """

    print(f"Processing: {json_file.name}")

    try:
        with open(json_file, 'r') as f:
            schema_body = json.load(f)
    except Exception as e:
        print(f"::error:: {json_file}: Failed to load: {str(e)}", file=sys.stderr)
        return None

    schema_name = json_file.name.replace('.json', '')

    print(f"  Schema Name: {schema_name}")
    print(f"  Version: {version}")

    try:
        schema = JSONSchema(
            organization_name=org_name,
            name=schema_name
        )

        schema.store(
            schema_body=schema_body,
            version=version,
            synapse_client=syn
        )
        print(f"✓ Registered: {schema_name} version {version}")

        return schema

    except Exception as e:
        print(f"::error:: {json_file}: Failed to register: {str(e)}", file=sys.stderr)
        return None


if __name__ == "__main__":
    main()
