# Function: country code (str, user input)
# ->
# Country name: Option<str>

import pycountry


def process_code(code: str) -> pycountry.db.Country | None:
    """
    Input: country code given by the user (str)
    Output: pycountry.db.Country | None
    """
    return pycountry.countries.get(alpha_2=code)


def country_name(opt_country: pycountry.db.Country | None) -> str | None:
    """
    Input: opt_country: pycountry.db.Country | None
    Output: The country's name (str | None)
    """
    if opt_country is None:
        return None
    return opt_country.name


def code2opt_name(code: str) -> str | None:
    """ Composition of the previous functions
    """
    opt_country = process_code(code)
    return country_name(opt_country)


def main():
    code = input("Enter country code: ")
    print(code2opt_name(code))


if __name__ == "__main__":
    main()
