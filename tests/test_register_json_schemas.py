import uuid
import sys
import os
from pathlib import Path
import pytest
from synapseclient.models import SchemaOrganization
from synapseclient import Synapse
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from register_json_schemas import main



@pytest.fixture(scope="module")
def schema_organization(request) -> SchemaOrganization:
    """Create a test organization for schema registration."""

    syn = Synapse()
    syn.login()

    org_name = f"test.org.id{str(uuid.uuid4())[:8]}"
    organization = SchemaOrganization(org_name)
    organization.store(synapse_client=syn)

    def cleanup():
        for schema in organization.get_json_schemas(synapse_client=syn):
            schema.delete(synapse_client=syn)
        organization.delete(synapse_client=syn)

    request.addfinalizer(cleanup)
    return organization


@pytest.fixture(scope="function")
def empty_folder_path(request) -> str:
    """Create an empty folder for testing."""
    directory_path = "empty_test_dir"

    os.makedirs(directory_path)

    def cleanup():
        os.rmdir(directory_path)

    request.addfinalizer(cleanup)
    return directory_path


def test_register_json_schemas(
    monkeypatch, capsys, schema_organization: SchemaOrganization
) -> None:
    """Integration test for registering JSON schemas from a directory."""

    monkeypatch.setenv('ORG_NAME', schema_organization.name)
    monkeypatch.setenv('VERSION', 'v1.0.0')
    monkeypatch.setenv('SCHEMA_DIR', './tests/schema_dir')

    assert main() == 0

    captured = capsys.readouterr()
    assert "Registered: Patient version 1.0.0" in captured.out


def test_register_json_schemas_no_version_env_var(monkeypatch, capsys) -> None:
    """Integration test for registering JSON schemas from a directory."""

    monkeypatch.delenv('VERSION', raising=False)
    monkeypatch.setenv('ORG_NAME', 'test_org')
    monkeypatch.setenv('SCHEMA_DIR', './tests/schema_dir')

    assert main() == 1

    captured = capsys.readouterr()
    assert "::error:: VERSION environment variable is required" in captured.err


def test_register_json_schemas_no_org_env_var(monkeypatch, capsys) -> None:
    """Integration test for registering JSON schemas from a directory."""

    monkeypatch.delenv('ORG_NAME', raising=False)
    monkeypatch.setenv('VERSION', '1.0.0')
    monkeypatch.setenv('SCHEMA_DIR', './tests/schema_dir')

    assert main() == 1

    captured = capsys.readouterr()
    assert "::error:: ORG_NAME environment variable is required" in captured.err


def test_register_json_schemas_no_schema_dir_env_var(monkeypatch, capsys) -> None:
    """Integration test for registering JSON schemas from a directory."""

    monkeypatch.delenv('SCHEMA_DIR', raising=False)
    monkeypatch.setenv('ORG_NAME', 'test_org')
    monkeypatch.setenv('VERSION', '1.0.0')

    assert main() == 1

    captured = capsys.readouterr()
    assert "::error:: SCHEMA_DIR environment variable is required" in captured.err


def test_register_json_schemas_org_does_not_exist(monkeypatch, capsys) -> None:
    """Integration test for registering JSON schemas from a directory."""

    monkeypatch.setenv('ORG_NAME', "not_a_real_org")
    monkeypatch.setenv('VERSION', '1.0.0')
    monkeypatch.setenv('SCHEMA_DIR', './tests/schema_dir')

    assert main() == 1

    captured = capsys.readouterr()
    assert "::error:: Organization not found: not_a_real_org" in captured.err


def test_register_json_schemas_dir_does_not_exist(
    monkeypatch, capsys, schema_organization: SchemaOrganization
) -> None:
    """Integration test for registering JSON schemas from a directory."""

    monkeypatch.setenv('ORG_NAME', schema_organization.name)
    monkeypatch.setenv('VERSION', '1.0.0')
    monkeypatch.setenv('SCHEMA_DIR', 'not_a_real_directory')

    assert main() == 1

    captured = capsys.readouterr()
    assert "::error:: Schema directory not found" in captured.err


def test_register_json_schemas_empty_dir(
    monkeypatch, capsys, schema_organization: SchemaOrganization, empty_folder_path: str
) -> None:
    """Integration test for registering JSON schemas from a directory."""

    monkeypatch.setenv('ORG_NAME', schema_organization.name)
    monkeypatch.setenv('VERSION', '1.0.0')
    monkeypatch.setenv('SCHEMA_DIR', empty_folder_path)

    assert main() == 1

    captured = capsys.readouterr()
    assert "::error:: No JSON files found in: empty_test_dir" in captured.err


def test_register_json_schemas_with_non_json(
    monkeypatch, capsys, schema_organization: SchemaOrganization
) -> None:
    """Integration test for registering JSON schemas from a directory."""

    monkeypatch.setenv('ORG_NAME', schema_organization.name)
    monkeypatch.setenv('VERSION', '1.0.0')
    monkeypatch.setenv('SCHEMA_DIR', './tests/non_schema_dir')

    assert main() == 1

    captured = capsys.readouterr()
    assert "::error:: tests/non_schema_dir/Patient.json: Failed to load: Expecting value: line 1 column 1 (char 0)" in captured.err


def test_register_json_schemas_with_malformed_json(
    monkeypatch, capsys, schema_organization: SchemaOrganization
) -> None:
    """Integration test for registering JSON schemas from a directory."""

    monkeypatch.setenv('ORG_NAME', schema_organization.name)
    monkeypatch.setenv('VERSION', '1.0.0')
    monkeypatch.setenv('SCHEMA_DIR', './tests/malformed_schema_dir')

    assert main() == 1

    captured = capsys.readouterr()
    assert "::error:: tests/malformed_schema_dir/Patient.json: Failed to register: 400 Client Error: JSON Element in Entity is Unsupported: non_keyword" in captured.err