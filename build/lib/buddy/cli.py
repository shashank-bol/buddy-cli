import click
import os
from .comet import comet
from .cw import cw
from .creds import creds

@click.command()
@click.option("--t", "--type" , default = None, help="possible values are - comet, cw/cloudwatch, tf, creds")
@click.option("--e", '--env', default=None, help="env name")
@click.option("--p", '--profile', default=None, help="aws creentials profile")
@click.option("--m", '--mode', default=None, help="comet mode")
@click.option("--c", '--create',default=None, help="create a new file pass snippet name using -s")
@click.option("--s",'--snippet', default=None, help="name of snippet")
@click.option("--d",'--delete', default=None, help="name of snippet file to be deleted (with extention)")
def cli(t,e,p,m,c,s,d):
    if t == "comet":
        comet.run(m , e , p)
    elif t == "cw" or t == "cloudwatch":
        cw.run(e , p)
    elif t == "creds":
        creds.run()
    else:
        click.echo('Welcome to buddy')