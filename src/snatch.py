#!/usr/bin/env python3
#
# A helper tool to retrieve the Tokens required by AzureHound. It relies on the
# Azure PowerShell app (client id `1950a258-227b-4e31-a9cf-717495945fc2`) which
# is available by default to all users.
#
# Reference:
# https://bloodhound.readthedocs.io/en/latest/data-collection/azurehound.html
#

import requests
import sys
from dataclasses import dataclass
from termcolor import colored
from datetime import datetime

#
# Constants
#

DEVICE_API_ENDPOINT = "https://login.microsoftonline.com/common/oauth2/devicecode?api-version=1.0"
TOKEN_API_ENDPOINT = "https://login.microsoftonline.com/Common/oauth2/token?api-version=1.0"
PROMPT_OK = colored('[+]', 'green')
PROMPT_ERR = colored('[!]', 'red')
GREEN_LINE = colored('-', 'green') * 80


#
# Data classes mapping output from Azure API endpoints to JSON.
#

@dataclass
class DeviceCode:
    user_code: str
    device_code: str
    verification_url: str


@dataclass
class AzToken:
    resource: str
    expires_on: str
    access_token: str
    refresh_token: str


def get_device_code(url: str) -> DeviceCode:
    """
    Uses the Azure Device Code API endpoint to retrieve a Device Code (required
    for completing the OAuth authentication flow).
    """

    body = {
        "client_id": "1950a258-227b-4e31-a9cf-717495945fc2",
        "resource": "https://graph.microsoft.com"
    }

    res = requests.post(url, data=body)

    if res.ok:
        try:
            data = res.json()
            return DeviceCode(
                user_code=data["user_code"],
                device_code=data["device_code"],
                verification_url=data["verification_url"]
            )
        except Exception as e:
            print(f"Fatal error: {e}")
            sys.exit(1)
    else:
        print(f"{PROMPT_ERR} Error: HTTP/S status code {res.status_code}")
        sys.exit(1)


def get_az_token(url, device_code: str) -> AzToken:
    """
    Get Azure Tokens using the Azure Token API endpoint. Requires a device code
    previously retrieved from the Azure Device Code API.
    """

    body = {
        "client_id": "1950a258-227b-4e31-a9cf-717495945fc2",
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        "code": device_code
    }

    res = requests.post(url, data=body)

    if res.ok:
        try:
            data = res.json()
            # Convert time from Unix timestamp to string
            expires_on = datetime.fromtimestamp(int(data["expires_on"]))
            expires_on = datetime.strftime(expires_on, "%c")
            return AzToken(
                resource=data["resource"],
                expires_on=expires_on,
                access_token=data["access_token"],
                refresh_token=data["refresh_token"]
            )
        except Exception as e:
            print(f"{PROMPT_ERR} Error: {e}")
            sys.exit(1)
    else:
        print(f"{PROMPT_ERR} Error: HTTP/S status code {res.status_code}")
        sys.exit(1)


def main():
    """
    Application entry point.
    """

    print(GREEN_LINE)
    print(f"{PROMPT_OK} Retrieving Azure Tokens to be used with AzureHound")
    print(GREEN_LINE)

    # Get device API response.
    device = get_device_code(DEVICE_API_ENDPOINT)

    # Guide user through next steps.
    verification_url = colored(device.verification_url, 'blue')
    user_code = colored(device.user_code, 'red', attrs=['bold'])
    print(f"{PROMPT_OK} Navigate to
          {verification_url} to authenticate yourself.")
    print(f"{PROMPT_OK} When asked, provide the following code: {user_code}")
    input(f"{PROMPT_OK} Once done, press any key to continue... ")

    # Get token API response.
    token = get_az_token(TOKEN_API_ENDPOINT, device.device_code)

    # Print results.
    print(GREEN_LINE)
    print(f"{PROMPT_OK} YOUR TOKENS:")
    print(f"{PROMPT_OK} > Expire on {token.expires_on}")
    print(f"{PROMPT_OK} > Resource: {token.resource}")
    print(f"{colored('[Access Token]', 'green', attrs=['bold'])}")
    print(f"{colored(token.access_token, 'magenta')}")
    print(f"{colored('[Refresh Token]', 'green', attrs=['bold'])}")
    print(f"{colored(token.refresh_token, 'magenta')}")
    print(GREEN_LINE)
    print(f"{PROMPT_OK} Happy hacking!")


if __name__ == "__main__":
    main()
