from src.version import get_version_info


def test_get_version_info_returns_expected_keys():
    version_info = get_version_info()

    assert {
        "app_name",
        "app_version",
        "app_stage",
        "build_label",
        "deployment_env",
        "git_commit",
    }.issubset(version_info)


def test_version_values_are_not_empty():
    version_info = get_version_info()

    assert version_info["app_version"]
    assert version_info["app_stage"]
