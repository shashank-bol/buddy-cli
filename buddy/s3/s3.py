import click
import os
def run(operation,profile,s3path, file):
    if profile is None:
        click.echo("Enter a Profile name")
        return
    if s3path is None:
        return click.echo("no s3path input")
    if operation is None:
        return click.echo("no s3path input")
    # if file is None:
    #     return click.echo("no prefix input")
    if operation == "u" or operation == "upload":
        os.system(f"aws s3 --profile {profile} cp {file} {s3path}")
        click.echo("file copied to s3 successfully")
    elif operation == "h" or operation == "head":
        os.system(f"aws s3 --profile {profile} head-object {s3path}")