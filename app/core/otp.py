import secrets
import hashlib


def generate_otp():
    return str(secrets.randbelow(900000) + 100000)


def hash_otp(otp: str):
    return hashlib.sha256(otp.encode()).hexdigest()


def verify_otp(otp: str, stored_hash: str):
    return hash_otp(otp) == stored_hash