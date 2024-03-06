import boto3
import webbrowser
from os import path
import click
def run():
    user_dir = path.expanduser("~")
    sso_oidc_client = boto3.client('sso-oidc',region_name = 'us-west-2')

    res = sso_oidc_client.register_client(
        clientName='macbook',
        clientType='public',
        scopes=[
            'write',
        ]
    )

    client_id = res["clientId"]

    client_secret = res["clientSecret"]

    start_url = "https://lji.awsapps.com/start#/"

    res2 = sso_oidc_client.start_device_authorization(
        clientId=client_id,
        clientSecret=client_secret,
        startUrl=start_url
    )

    device_code = res2["deviceCode"]

    user_code = res2["userCode"]

    verification_uri = res2["verificationUri"]

    click.echo("Enter this code in browser and verify : " + str(user_code))

    webbrowser.open(verification_uri)

    click.prompt("Press enter after authorization is completed")

    res3 = sso_oidc_client.create_token(
        clientId=client_id,
        clientSecret=client_secret,
        grantType="urn:ietf:params:oauth:grant-type:device_code",
        deviceCode=device_code,
        # code=user_code,
        # refreshToken='string',
        # scope=[
        #     'string',
        # ],
        # redirectUri='string'
    )

    print(res3)

    access_token = res3["accessToken"]

    token_type = res3["tokenType"]


    sso = boto3.client("sso", region_name="us-west-2")

    res4 = sso.list_accounts(accessToken=access_token)

    account_list = res4["accountList"]

    account_roles = []

    for account in account_list:
        res5 = sso.list_account_roles(accessToken=access_token,accountId = account["accountId"])
        account_roles.append(list(map( lambda x : x["roleName"],res5["roleList"] )))

    with open(user_dir + "/.aws/credentials",'w') as f:
        for i in range(len(account_list)):
            for role in account_roles[i]:
                aname = account_list[i]["accountName"]
                f.write("["+aname.replace(" ","") + role + "]\n")
                res6 = sso.get_role_credentials(
                    roleName=role,
                    accountId=account_list[i]["accountId"],
                    accessToken=access_token
                )
                access_key_id = res6["roleCredentials"]["accessKeyId"]
                secret_access_key = res6["roleCredentials"]["secretAccessKey"]
                session_token = res6["roleCredentials"]["sessionToken"]
                f.write(f"aws_access_key_id={access_key_id}\n")
                f.write(f"aws_secret_access_key={secret_access_key}\n")
                f.write(f"aws_session_token={session_token}\n")
        f.close()
