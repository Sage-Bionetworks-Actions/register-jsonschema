# Register JSON Schema

[![Continuous Integration](https://github.com/Sage-Bionetworks-Actions/register-jsonschema/actions/workflows/ci.yml/badge.svg)](https://github.com/Sage-Bionetworks-Actions/register-jsonschema/actions/workflows/ci.yml)

Register JSON Schema files with Synapse using the Synapse Python client.

This action is intended to be used in conjunction with the [Generate JSON Schemas](https://github.com/Sage-Bionetworks-Actions/generate-jsonschema) action, which generates JSON Schema files from a data model.

## Usage

```yaml
steps:
  - name: Register Schemas
    uses: Sage-Bionetworks-Actions/register-jsonschema@v1
    with:
      org-name: 'my.organization'
      schema-dir: './schemas'
      version: '1.0.0'
      synapse_auth_token: ${{ secrets.SYNAPSE_AUTH_TOKEN }}
```

## Inputs

| Name | Description | Required |
| --- | --- | --- | --- |
| `org-name` | Your Synapse username. | Yes |
| `schema-dir` | Your Synapse password or Personal Access Token (PAT). | Yes |
| `version` | The local path to the JSON schema file to be registered. | No |
| `synapse-auth-token` | A description for the schema being registered. | Yes |

---

## Example Workflow

The following example workflow starts with JSON Schema in a directory and registers them to Synapse.

```yaml
name: CI

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        id: checkout
        uses: actions/checkout@v4

      - name: Register JSON Schema
        id: register
        uses: Sage-Bionetworks-Actions/register-jsonschema@v1
        with:
          org-name: your_org_name
          schema-dir: your_schema_directory
          synapse_auth_token: ${{ secrets.SYNAPSE_AUTH_TOKEN }}
          version: 1.0.0


```

The following example demonstrates a full workflow that generates a schema using the companion action and then registers it to Synapse.

```yaml
name: CI

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        id: checkout
        uses: actions/checkout@v6

      - name: Generate JSON Schemas
        id: generate
        uses: Sage-Bionetworks-Actions/generate-jsonschema@main
        with:
          data-model-source: ./tests/data_model.csv
          data-model-labels: "display_label"

      - name: Register JSON Schemas
        id: register
        uses: ./
        with:
          org-name: dpetest
          schema-dir: ${{ steps.generate.outputs.schemas}}
          synapse-auth-token: ${{ secrets.SYNAPSE_AUTH_TOKEN }}


```

## License

This project is licensed under the [Apache 2.0 License](https://www.google.com/search?q=LICENSE).
