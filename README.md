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

| Input | Description | Required |
| :--- | :--- | :--- |
| `org-name` | Name of the Synapse organization to register schemas in. | `true` |
| `schema-dir` | Path to directory containing JSON schema files. | `true` |
| `version` | Semantic version of the schemas being registered. | `false` |
| `synapse-auth-token` | Synapse Personal Access Token with permissions to register schemas in the Synapse organization. | `true` |

## Outputs

| Output | Description |
| :--- | :--- |
| `uris` | URIs of registered schemas. |

## Example Workflow

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
        uses: Sage-Bionetworks-Actions/register-jsonschema@v1
        with:
          org-name: dpetest
          schema-dir: ${{ steps.generate.outputs.schemas}}
          synapse-auth-token: ${{ secrets.SYNAPSE_AUTH_TOKEN }}

```

## License

This project is licensed under the [Apache 2.0 License](https://www.google.com/search?q=LICENSE).
