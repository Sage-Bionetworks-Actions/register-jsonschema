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
def synapse_client() -> Synapse:
    """Create a Synapse client for testing."""
    syn = Synapse()
    syn.login()
    return syn


@pytest.fixture(scope="module")
def schema_organization(request, synapse_client: Synapse) -> SchemaOrganization:
    """Create a test organization for schema registration."""
    org_name = f"test.org.id{str(uuid.uuid4())[:8]}"
    organization = SchemaOrganization(org_name)
    organization.store(synapse_client=synapse_client)

    def cleanup():
        for schema in organization.get_json_schemas(synapse_client=synapse_client):
            schema.delete(synapse_client=synapse_client)
        organization.delete(synapse_client=synapse_client)

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


@pytest.fixture(scope="function")
def text_file_path(request) -> str:
    """Create an empty folder for testing."""
    path = "text.txt"

    def cleanup():
        if os.path.exists(path):
            os.remove(path)

    request.addfinalizer(cleanup)
    return path


class TestRegisterJsonSchemas:

    @pytest.fixture(autouse=True, scope="function")
    def init(
        self,
        monkeypatch,
        schema_organization: SchemaOrganization,
        text_file_path: str
    ) -> None:
        monkeypatch.setenv('ORG_NAME', schema_organization.name)
        monkeypatch.setenv('VERSION', 'v1.0.0')
        monkeypatch.setenv('SCHEMA_DIR', './tests/schema_dir')
        monkeypatch.setenv('GITHUB_OUTPUT', text_file_path)

    def test_success(self, capsys, text_file_path: str) -> None:
        """Integration test for registering JSON schemas from a directory."""
        main()
        captured = capsys.readouterr()
        assert "Fix Schema Name: False" in captured.out
        assert "Registered: Patient version 1.0.0" in captured.out
        assert "Registered: Biospecimen version 1.0.0" in captured.out
        assert os.path.exists(text_file_path)

    def test_success_no_version_env_var(
        self, monkeypatch, capsys, text_file_path: str
    ) -> None:
        """Integration test for registering JSON schemas from a directory."""
        monkeypatch.delenv('VERSION', raising=False)
        main()
        captured = capsys.readouterr()
        assert "Registered: Patient version None" in captured.out
        assert "Registered: Biospecimen version None" in captured.out
        assert os.path.exists(text_file_path)

    def test_success_fix_schema_name(self, monkeypatch,  capsys, text_file_path: str) -> None:
        """Integration test for registering JSON schemas from a directory."""
        monkeypatch.setenv('FIX_SCHEMA_NAME', "true")
        monkeypatch.setenv('SCHEMA_DIR', './tests/schema_dir_bad_names')
        main()
        captured = capsys.readouterr()
        assert "Fix Schema Name: True" in captured.out
        assert "Changed schema name from 'Patient-Schema' to 'PatientSchema'" in captured.out
        assert "Changed schema name from 'Biospecimen_Schema' to 'BiospecimenSchema'" in captured.out
        assert "Registered: PatientSchema version 1.0.0" in captured.out
        assert "Registered: BiospecimenSchema version 1.0.0" in captured.out
        assert os.path.exists(text_file_path)

    def test_no_org_env_var(self, monkeypatch, capsys) -> None:
        """Integration test for registering JSON schemas from a directory."""
        monkeypatch.delenv('ORG_NAME', raising=False)
        with pytest.raises(SystemExit) as exit:
            main()
        assert exit.type is SystemExit
        assert exit.value.code == 1
        captured = capsys.readouterr()
        assert "::error:: ORG_NAME environment variable is required" in captured.err

    def test_no_schema_dir_env_var(self, monkeypatch, capsys) -> None:
        """Integration test for registering JSON schemas from a directory."""
        monkeypatch.delenv('SCHEMA_DIR', raising=False)
        with pytest.raises(SystemExit) as exit:
            main()
        assert exit.type is SystemExit
        assert exit.value.code == 1
        captured = capsys.readouterr()
        assert "::error:: SCHEMA_DIR environment variable is required" in captured.err

    def test_org_does_not_exist(self, monkeypatch, capsys) -> None:
        """Integration test for registering JSON schemas from a directory."""
        monkeypatch.setenv('ORG_NAME', "not_a_real_org")
        with pytest.raises(SystemExit) as exit:
            main()
        assert exit.type is SystemExit
        assert exit.value.code == 1
        captured = capsys.readouterr()
        assert "::error:: Organization not found: not_a_real_org" in captured.err

    def test_dir_does_not_exist(self, monkeypatch, capsys) -> None:
        """Integration test for registering JSON schemas from a directory."""
        monkeypatch.setenv('SCHEMA_DIR', 'not_a_real_directory')
        with pytest.raises(SystemExit) as exit:
            main()
        assert exit.type is SystemExit
        assert exit.value.code == 1
        captured = capsys.readouterr()
        assert "::error:: Schema directory not found" in captured.err

    def test_empty_dir(self, monkeypatch, capsys, empty_folder_path: str) -> None:
        """Integration test for registering JSON schemas from a directory."""
        monkeypatch.setenv('SCHEMA_DIR', empty_folder_path)
        with pytest.raises(SystemExit) as exit:
            main()
        assert exit.type is SystemExit
        assert exit.value.code == 1
        captured = capsys.readouterr()
        assert "::error:: No JSON files found in: empty_test_dir" in captured.err

    def test_non_json(self, monkeypatch, capsys) -> None:
        """Integration test for registering JSON schemas from a directory."""
        monkeypatch.setenv('SCHEMA_DIR', './tests/non_schema_dir')
        with pytest.raises(SystemExit) as exit:
            main()
        assert exit.type is SystemExit
        assert exit.value.code == 1
        captured = capsys.readouterr()
        assert "::error:: tests/non_schema_dir/Patient.json: Failed to register: Expecting value: line 1 column 1 (char 0)" in captured.err

    def test_malformed_json(self, monkeypatch, capsys) -> None:
        """Integration test for registering JSON schemas from a directory."""
        monkeypatch.setenv('SCHEMA_DIR', './tests/malformed_schema_dir')
        with pytest.raises(SystemExit) as exit:
            main()
        assert exit.type is SystemExit
        assert exit.value.code == 1
        captured = capsys.readouterr()
        assert "::error:: tests/malformed_schema_dir/Patient.json: Failed to register: 400 Client Error: JSON Element in Entity is Unsupported: non_keyword" in captured.err
