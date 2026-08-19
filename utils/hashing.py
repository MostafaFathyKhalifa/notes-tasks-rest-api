from argon2 import PasswordHasher

password = PasswordHasher()


def hash_password(password_str: str) -> str:
    """
    Hashes a password using Argon2.

    Args:
        password_str (str): The password to hash.

    Returns:
        str: The hashed password.
    """
    return password.hash(password_str)


def verify_password(hashed_password: str, password_str: str) -> bool:
    from argon2.exceptions import InvalidHash, VerificationError, VerifyMismatchError

    """
    Verifies a password against a hashed password.

    Args:
        hashed_password (str): The hashed password.
        password_str (str): The password to verify.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    try:
        check_password = password.verify(hashed_password, password_str)
        print("Password verification successful.")
        return check_password
    except VerifyMismatchError:
        print("Password verification failed: Mismatch.")
        return False
    except InvalidHash:
        print("Password verification failed: Invalid hash.")
        return False
    except VerificationError:
        print("Password verification failed: Verification error.")
        return False
