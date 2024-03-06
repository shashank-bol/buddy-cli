from datetime import datetime, timedelta
import boto3
import time
import click
from tabulate import tabulate

def get_logs(log_group , query , limit, region, hours, profile):
    session = boto3.Session(profile_name=profile)
    client = session.client('logs',region_name = region)
    start_query_response = client.start_query(
    logGroupName=log_group,
    startTime=int(
            (datetime.today() - timedelta(hours=hours)).timestamp()
        ),
        endTime=int(datetime.now().timestamp()),
        queryString=query,
        limit=limit,
    )
    query_id = start_query_response['queryId']
    response = None
    while response == None or response['status'] == 'Running':
        print('Waiting for query to complete ...')
        time.sleep(2)
        response = client.get_query_results(queryId=query_id)
    return response


def get_region_by_env(env:str)->str:
    env = env.lower()
    if env in ["qa","qav2","qav3","qav5","pqa","pqa2"]:
        return "us-west-2"
    if env == "demov5":
        return "ap-southeast-1"
    elif env == "qav4" or env == "ie":
        return "eu-west-1"
    elif "devint" in env:
        i = 1 if env == "devint" else int(env.lstrip("devint"))
        if i < 8:
            return "us-west-2"
        elif i >= 8 and i<=17:
            return "eu-west-1"
        elif i>=17 and i<=25:
            return "eu-central-1"
        elif i>=26 and i<=32:
            return "us-west-2"
        elif i == 33:
            return "ap-southeast-1"
        elif i == 34:
            return "eu-central-1"
        else:
            raise ValueError("Cannot find region for this environment")
    elif "apm" in env:
        return "ap-south-1"
    elif "cac" in env:
        return "ca-central-1"
    elif "aps" in env:
        return "ap-southeast-1"
    elif "eui" in env:
        return "eu-west-1"
    elif "euf" in env:
        return "eu-central-1"
    elif "prod" in env or "demo" in env or "uso" in env:
        return "us-west-2"
    else :
        raise ValueError("Cannot find region for this environment")
   


def run(env , profile):
    if env is None:
        return click.echo("please enter an env")
    if profile is None:
        return click.echo("please enter a profile")
    region = get_region_by_env(env.lower())
    log_group = click.prompt("Enter log group")
    hours = click.prompt("search log for last n hours",type=int)
    limit = click.prompt("limit(max 10k)",type=int)
    query = click.prompt("Enter query, enter ';' to stop")
    while not query.replace(' ',  '').endswith(';'):
        query = query + " " + click.prompt("...")
    query = query.rstrip(" ").rstrip(";")
    click.echo("running query: "  + query)
    response = get_logs(
        log_group=log_group,
        query=query,
        region=region,
        hours=hours,
        limit=limit,
        profile=profile
    )
    rows = []
    headers = []
    for i in range(0, len(response['results'])):
        row = []
        for x in response['results'][i]:
            if i == 0:
                headers.append(x['field'])
            row.append(x['value'])
        rows.append(row)
    
    click.echo(tabulate(rows,headers=headers))