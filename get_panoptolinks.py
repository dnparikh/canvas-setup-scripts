#!python3
"""Authorization sample, as Server-side Web Application."""
import sys
import argparse
import requests
import urllib3
import time
import json
import os

from dotenv import load_dotenv

# 🔐 Load API config from .env
load_dotenv()

server    = os.getenv("PANOPTO_URL")
client_id = os.getenv("PANOPTO_CLIENT_ID")
client_secret = os.getenv("PANOPTO_CLIENT_SECRET")

#from os.path import dirname, join, abspath
#sys.path.insert(0, abspath(join(dirname(__file__), '..', 'common')))
from panopto_oauth2 import PanoptoOAuth2


def parse_argument():
    parser = argparse.ArgumentParser(description='Get Panopto Video URLS')
    parser.add_argument('--folder', dest='folder_id', required=True, help='Get folder ID.')
    #parser.add_argument('--client-id', dest='client_id', required=True, help='Client ID of OAuth2 client')
    #parser.add_argument('--client-secret', dest='client_secret', required=True, help='Client Secret of OAuth2 client')
    parser.add_argument('--skip-verify', dest='skip_verify', action='store_true', required=False, help='Skip SSL certificate verification. (Never apply to the production code)')
    return parser.parse_args()


def main():
    """First function called from command line."""
    args = parse_argument()

    if args.skip_verify:
        # This line is needed to suppress annoying warning message.
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Use requests module's Session object in this example.
    # ref. https://2.python-requests.org/en/master/user/advanced/#session-objects
    requests_session = requests.Session()
    requests_session.verify = not args.skip_verify

    # Load OAuth2 logic
    oauth2 = PanoptoOAuth2(server, client_id, client_secret, not args.skip_verify)

    # Initial authorization
    authorization(requests_session, oauth2)

    # Call Panopto API (getting sub-folders from top level folder) repeatedly
    # folder_id = '00000000-0000-0000-0000-000000000000' # represent top level folder
    # folder_id = 'b47d5654-3614-4739-8f33-ab88010a51e3' # represents My Folder
    # folder_id = 'a78dc18b-9a6d-4650-a1f1-b30700752740' # CS311 sandbox

    folder_id   = args.folder_id

    # print('Calling GET /api/v1/folders/{0}/children endpoint'.format(folder_id))
    print('Calling GET /api/v1/folders/{0}/sessions endpoint'.format(folder_id))
    # url = 'https://{0}/Panopto/api/v1/folders/{1}/children'.format(args.server, folder_id)
    url = 'https://{0}/Panopto/api/v1/folders/{1}/sessions'.format(server, folder_id)
    resp = requests_session.get(url = url)
    if inspect_response_is_unauthorized(resp):
        # Re-authorization
        print('Re-authorization required')
        authorization(requests_session, oauth2)
    data = resp.json() # parse JSON format response
    print(json.dumps(data, indent=2, sort_keys=True))
    for folder in data["Results"]:
        print('  {0}: {1} {2}'.format(folder['Id'], folder['Name'], folder['Urls']['ViewerUrl']))
    time.sleep(1)
    print('done!')

def authorization(requests_session, oauth2):
    # Go through authorization
    access_token = oauth2.get_access_token_authorization_code_grant()
    # Set the token as the header of requests
    requests_session.headers.update({'Authorization': 'Bearer ' + access_token})

def inspect_response_is_unauthorized(response):
    '''
    Inspect the response of a requets' call, and return True if the response was Unauthorized.
    An exception is thrown at other error responses.
    Reference: https://stackoverflow.com/a/24519419
    '''
    if response.status_code // 100 == 2:
        # Success on 2xx response.
        return False

    if response.status_code == requests.codes.unauthorized:
        print('Unauthorized. Access token is invalid.')
        return True

    # Throw unhandled cases.
    response.raise_for_status()


if __name__ == '__main__':
    main()
