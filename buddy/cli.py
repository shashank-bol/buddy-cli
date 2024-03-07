import click
from .comet import comet
from .cw import cw
from .creds import creds
from .tf import tf
from .s3 import s3

@click.command()
@click.option("-t", "--type" , default = None, help="possible values are - comet, cw/cloudwatch, tf, creds")
@click.option("-e", '--env', default=None, help="env name")
@click.option("-p", '--profile', default=None, help="aws creentials profile")
@click.option("-m", '--mode', default=None, help="comet mode")
@click.option("-v",'--var', default=None,multiple=True, help="terraform var")
@click.option("-q",'--quit',is_flag=True ,default=False, help="close ports in comet")
@click.option("-o",'--operation',default=None, help="operation for s3")
@click.option("-d" , "--path" , default=None, help= "path for s3")
@click.option("-f" , "--file" , default=None, help= "file for s3")
def cli(type,env,profile,mode,var,quit,operation,path,file):
    if type == "comet":
        comet.run(mode , env , profile, quit)
    elif type == "cw" or type == "cloudwatch":
        cw.run(env , profile)
    elif type == "creds":
        creds.run()
    elif type == "tf":
        tf.run(env , var)
    elif type == "s3":
        s3.run(operation, profile , path, file)
    else:
        print("Welcome to buddy")