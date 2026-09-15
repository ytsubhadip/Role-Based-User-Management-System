# app/core/password_generator.py

import secrets
import string


def generate_temporary_password(length: int = 12):
    characters = (
        string.ascii_letters
        + string.digits

    )

    return "".join(
        secrets.choice(characters)
        for _ in range(length)
    )



if __name__ == "__main__":
    temp_password = generate_temporary_password()
    print(f"Temporary password: {temp_password}")