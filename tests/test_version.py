from src.version import get_version_info


def test_get_version_info_returns_expected_keys(monkeypatch):
    monkeypatch.delenv("RESUMEIQ_APP_ENV", raising=False)
    monkeypatch.delenv("RESUMEIQ_GIT_COMMIT", raising=False)
    version_info = get_version_info()

    assert {
        "app_name",
        "app_version",
        "app_stage",
        "deployment_env",
        "git_commit",
    }.issubset(version_info)
    assert "build_label" not in version_info


def test_version_values_are_not_empty():
    version_info = get_version_info()

    assert version_info["app_version"]
    assert version_info["app_stage"]


def test_get_version_info_defaults_to_local(monkeypatch):
    monkeypatch.delenv("RESUMEIQ_APP_ENV", raising=False)
    monkeypatch.delenv("RESUMEIQ_GIT_COMMIT", raising=False)

    version_info = get_version_info()

    assert version_info["deployment_env"] == "local"
    assert version_info["git_commit"] == "local"


def test_get_version_info_uses_environment_overrides(monkeypatch):
    monkeypatch.setenv("RESUMEIQ_APP_ENV", "azure")
    monkeypatch.setenv("RESUMEIQ_GIT_COMMIT", "0026fe9")

    version_info = get_version_info()

    assert version_info["deployment_env"] == "azure"
    assert version_info["git_commit"] == "0026fe9"
