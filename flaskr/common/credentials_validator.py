import re


class CredentialsValidator:
    EMAIL_REGEX = re.compile(
        "(?:[a-z0-9!#\$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#\$%&'*+/=?^_`{|}~-]+)*|\"(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21\\x23-\\x5b\\x5d-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])*\")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x21-\\x5a\\x53-\\x7f]|\\\\[\\x01-\\x09\\x0b\\x0c\\x0e-\\x7f])+)\\])"  # noqa: E501
    )

    USERNAME_REGEX = re.compile("^[a-zA-Z0-9_]{5,20}$")

    @classmethod
    def validate_username(cls, username: str) -> bool:
        return cls.USERNAME_REGEX.match(username)

    @classmethod
    def validate_email(cls, email: str) -> bool:
        return cls.EMAIL_REGEX.match(email)

    @staticmethod
    def validate_password(password: str) -> bool:
        return 8 <= len(password) <= 20
