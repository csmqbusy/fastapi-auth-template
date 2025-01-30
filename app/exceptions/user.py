class UserException(Exception):
    pass


class UniqueViolation(UserException):
    pass


class UsernameAlreadyExists(UniqueViolation):
    pass


class EmailAlreadyExists(UniqueViolation):
    pass
