"""
Register JSON schemas to Synapse organization.

This script registers JSON schemas from a directory to a Synapse organization.
The semantic version is passed as a parameter, NOT included in the schema name.
"""

import os

import sys
from pathlib import Path

from synapseclient import Synapse
from synapseclient.models import JSONSchema, SchemaOrganization
from synapseclient.extensions.curator import register_jsonschema


def main() -> None:
    """
    Main function to generate JSON schemas from data models.
    Expects the following environment variables:
    - ORG_NAME: Organization name
    - SCHEMA_DIR: Directory containing JSON schemas
    - SYNAPSE_AUTH_TOKEN: Synapse Personal Access Token.
      - Not required for local testing.
    Can use the following optional environment variables:
    - VERSION: Semantic version (e.g., '1.0.0')
    - GITHUB_OUTPUT: JSON schema URIs will be appended to this
        file in GitHub Actions output format.




    """
    org_name = os.environ.get("ORG_NAME")
    schema_dir = os.environ.get("SCHEMA_DIR")
    github_output = os.environ.get('GITHUB_OUTPUT', None)
    synapse_pat = os.environ.get("SYNAPSE_AUTH_TOKEN", None)
    version = os.environ.get("VERSION", None)

    syn = Synapse()
    syn.login()

    if not org_name:
        print("::error:: ORG_NAME environment variable is required", file=sys.stderr)
        sys.exit(1)

    if not schema_dir:
        print("::error:: SCHEMA_DIR environment variable is required", file=sys.stderr)
        sys.exit(1)

    print(f"\n{'='*60}")
    print("JSON Schema Registration")
    print(f"{'='*60}")
    if synapse_pat:
        print("Synapse PAT is set")
    else:
        print("Synapse PAT is not set")
    print(f"Organization: {org_name}")
    print(f"Version: {version}")
    print(f"Schema Directory: {schema_dir}")
    print(f"{'='*60}\n")

    if version and version.startswith('v'):
        version = version[1:]

    try:
        org = SchemaOrganization(name=org_name)
        org.get(synapse_client=syn)
        print(f"✓ Organization found: {org_name}\n")
    except Exception as e:
        print(f"::error:: Organization not found: {org_name}", file=sys.stderr)
        print(f"::error:: {str(e)}", file=sys.stderr)
        sys.exit(1)

    schema_dir = Path(schema_dir)
    if not schema_dir.exists():
        print(f"::error:: Schema directory not found: {schema_dir}", file=sys.stderr)
        sys.exit(1)

    json_files = list(schema_dir.glob("*.json"))
    if not json_files:
        print(f"::error:: No JSON files found in: {schema_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(json_files)} JSON schema file(s)\n")

    success_count = 0
    failed_count = 0

    results = []
    for json_file in sorted(json_files):
        result = register_schema(syn, json_file, org_name, version)
        results.append(result)

        if result:
            success_count += 1
        else:
            failed_count += 1

    if github_output:
        uris = [schema.uri for schema in results if schema is not None]
        with open(github_output, 'a') as file:
            file.write("uris<<EOF\n")
            file.write('\n'.join(uris))
            file.write("\nEOF\n")

    print(f"{'='*60}")
    print("Registration Summary")
    print(f"{'='*60}")
    print(f"Total Processed: {len(json_files)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {failed_count}")
    print(f"{'='*60}")

    if failed_count > 0:
        sys.exit(1)


def register_schema(
    syn: Synapse, json_file: Path, org_name: str, version: str | None
) -> JSONSchema:
    """
    Register a single JSON schema to Synapse.

    Args:
        syn: Synapse client
        json_file: Path to JSON schema file
        org_name: Organization name
        version: Semantic version (e.g., '1.0.0')

    Returns:
        JSONSchema object if successful
    """

    print(f"Processing: {json_file.name}")

    schema_name = json_file.name.replace('.json', '')

    print(f"  Schema Name: {schema_name}")
    print(f"  Version: {str(version)}")

    try:
        schema = register_jsonschema(
            schema_path=str(json_file),
            organization_name=org_name,
            schema_name=schema_name,
            schema_version=version,
            synapse_client=syn
        )

        print(f"✓ Registered: {schema_name} version {str(version)}")
        return schema

    except Exception as e:
        print(f"::error:: {json_file}: Failed to register: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
    sys.exit(0)
