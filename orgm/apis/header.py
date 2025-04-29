import os


def get_headers_json():

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    CF_ACCESS_CLIENT_ID = os.getenv("CF_ACCESS_CLIENT_ID")
    CF_ACCESS_CLIENT_SECRET = os.getenv("CF_ACCESS_CLIENT_SECRET")

    if CF_ACCESS_CLIENT_ID and CF_ACCESS_CLIENT_SECRET:
        headers["CF-Access-Client-Id"] = CF_ACCESS_CLIENT_ID
        headers["CF-Access-Client-Secret"] = CF_ACCESS_CLIENT_SECRET

    return headers


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    print(get_headers_json())
