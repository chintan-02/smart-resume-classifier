from src.privacy_tools import mask_pii


def test_mask_email():
    text = "Email me at [test@example.com](mailto:test@example.com)"

    masked = mask_pii(text)

    assert "[email]" in masked
    assert "test@example.com" not in masked


def test_mask_phone():
    text = "Call me at (403) 555-0192"

    masked = mask_pii(text)

    assert "[phone]" in masked
    assert "555-0192" not in masked


def test_mask_linkedin_github():
    text = "linkedin.com/in/test github.com/test"

    masked = mask_pii(text)

    assert "[linkedin]" in masked
    assert "[github]" in masked


def test_mask_candidate_name_case_insensitive():
    text = "ARJUN MEHRA is a Data Scientist"

    masked = mask_pii(text, candidate_name="Arjun Mehra")

    assert "[candidate_name]" in masked
    assert "ARJUN MEHRA" not in masked


def test_mask_pii_combined():
    text = "Arjun Mehra can be reached at arjun@example.com, (403) 555-0192, linkedin.com/in/arjun."

    masked = mask_pii(text, candidate_name="Arjun Mehra")

    assert "[candidate_name]" in masked
    assert "[email]" in masked
    assert "[phone]" in masked
    assert "[linkedin]" in masked
    assert "arjun@example.com" not in masked
