import os

import requests
from dotenv import load_dotenv


load_dotenv()


def required_env(name):
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is missing in .env")
    return value


def get_access_token():
    response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": required_env("GOOGLE_CLIENT_ID"),
            "client_secret": required_env("GOOGLE_CLIENT_SECRET"),
            "refresh_token": required_env("GOOGLE_REFRESH_TOKEN"),
            "grant_type": "refresh_token",
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def main():
    token = get_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    accounts_response = requests.get(
        "https://mybusinessaccountmanagement.googleapis.com/v1/accounts",
        headers=headers,
        timeout=30,
    )
    accounts_response.raise_for_status()
    accounts = accounts_response.json().get("accounts", [])

    if not accounts:
        print("No Google Business Profile accounts found for this OAuth user.")
        return

    for account in accounts:
        account_name = account["name"]
        account_id = account_name.split("/")[-1]
        print(f"\nAccount: {account.get('accountName', account_name)}")
        print(f"GOOGLE_ACCOUNT_ID={account_id}")

        locations_response = requests.get(
            f"https://mybusinessbusinessinformation.googleapis.com/v1/{account_name}/locations",
            headers=headers,
            params={"readMask": "name,title,storefrontAddress", "pageSize": 100},
            timeout=30,
        )
        locations_response.raise_for_status()
        locations = locations_response.json().get("locations", [])

        for location in locations:
            location_id = location["name"].split("/")[-1]
            print(f"  Location: {location.get('title', location['name'])}")
            print(f"  GOOGLE_LOCATION_ID={location_id}")


if __name__ == "__main__":
    main()
