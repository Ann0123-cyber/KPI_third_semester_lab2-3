"""
Unit-тести Value Objects — жодної БД, жодного фреймворку.
"""
import pytest
from app.domain.value_objects.email import Email
from app.domain.value_objects.username import Username
from app.domain.errors import InvalidEmailError, InvalidUsernameError


class TestEmail:
    def test_valid_email(self):
        e = Email("user@example.com")
        assert str(e) == "user@example.com"

    def test_emails_equal_by_value(self):
        assert Email("a@b.com") == Email("a@b.com")

    def test_different_emails_not_equal(self):
        assert Email("a@b.com") != Email("c@d.com")

    def test_invalid_email_raises_domain_error(self):
        with pytest.raises(InvalidEmailError):
            Email("not-an-email")

    def test_email_without_domain_invalid(self):
        with pytest.raises(InvalidEmailError):
            Email("user@")

    def test_email_is_immutable(self):
        e = Email("user@example.com")
        with pytest.raises(Exception):
            e.value = "other@example.com"


class TestUsername:
    def test_valid_username(self):
        u = Username("alice_99")
        assert str(u) == "alice_99"

    def test_usernames_equal_by_value(self):
        assert Username("bob") == Username("bob")

    def test_too_short_raises_error(self):
        with pytest.raises(InvalidUsernameError):
            Username("ab")

    def test_too_long_raises_error(self):
        with pytest.raises(InvalidUsernameError):
            Username("a" * 33)

    def test_special_chars_raise_error(self):
        with pytest.raises(InvalidUsernameError):
            Username("user name!")

    def test_username_is_immutable(self):
        u = Username("alice")
        with pytest.raises(Exception):
            u.value = "bob"