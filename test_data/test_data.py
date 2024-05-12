import random
import string
import datetime
from faker import Faker

def generate_fake_last_names(num_last_names: int) -> list:
    """
    generate n number of fake last names
    """

    fake = Faker()
    last_names = [fake.last_name() for _ in range(num_last_names)]
    return last_names


def generate_fake_last_name() -> str:
    """
    generate fake last name
    """

    fake = Faker()
    return fake.last_name()


def generate_fake_name() -> str:
    """
    generate fake name
    """
    fake = Faker()
    return fake.name()

def generate_random_number(lower_limit: int, upper_limit=1000) -> int:
    """
    Generates a random integer between lower_limit and upper_limit.
    """
    return random.randint(lower_limit, upper_limit)


def generate_random_request_id(length: int = 16) -> str:
    """
    Generates a random string of specified length for the request ID.
    """
    letters_and_digits = string.ascii_letters + string.digits
    return "".join(random.choice(letters_and_digits) for _ in range(length))


def get_current_date_header() -> str:
    """
    Returns the current date and time in HTTP header format.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.strftime("%a, %d %b %Y %H:%M:%S GMT")
