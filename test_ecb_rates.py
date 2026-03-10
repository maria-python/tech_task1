from pprint import pprint

from src.api.ecb_client import fetch_currency_rates
from src.processing.transform import transform_currency_data


if __name__ == "__main__":
    start_date = "2024-01-01"
    end_date = "2024-01-05"

    raw_data = fetch_currency_rates(start_date, end_date)
    transformed_data = transform_currency_data(raw_data)

    print("RAW DATA:")
    pprint(raw_data)

    print("\nTRANSFORMED DATA:")
    pprint(transformed_data)