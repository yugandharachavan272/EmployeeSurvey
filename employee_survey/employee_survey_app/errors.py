# pylint: disable=invalid-name
# pylint: disable=broad-except
# pylint: disable=missing-docstring
# pylint: disable=no-member
__all__ = ['PasswordError', 'AttemptExhausted']


class PasswordError(Exception):
    """
    This is Password error raised for wrong password
    """

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class AttemptExhausted(PasswordError):
    pass
