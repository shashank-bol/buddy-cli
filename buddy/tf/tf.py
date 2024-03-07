import os 
import click
import re
import json

def verify_plan(tag_map:dict,textplan:str) -> bool:
    jsonre = re.compile(r"\{[^\}]*?\}")
    all_plans = jsonre.findall(textplan)
    print(all_plans)
    valid_resources = ["lambda" , "ecs" , "batch" , "taskdefinition"]
    tag_re = re.compile("|".join(tag_map.keys()))
    for plan in all_plans:
        json_plan = json.load(plan)
        if json_plan["type"] == "planned_change":
            if json_plan["change"]["resource"]["resource_name"] not in valid_resources:
                return False
            if not tag_re.search(json_plan["change"]["resource"]["addr"]):
                return False
    return True


def run(env, tags):
    if env is None:
        return click.echo("Enter env")
    if tags is None or len(tags) == 0:
        return click.echo("Atleast one tag required")
    tag_map = dict()
    for tag in tags:
        if '=' not in tag:
            return click.echo('"=" missing in tag ' + tag )
        else:
            a = tag.split("=")
            if len(a) !=2:
                return click.echo('Error for value ' + tag +', it must follow pattern <tf_variable>=<value/tag>')
            tag_map[a[0]] = a[1]
    
    os.system("terraform plan -json --var-file=keys.tfvars" + " -var ".join(tags) +" > plan.txt")
    fl = open("plan.txt","r")
    plan = fl.read()
    if verify_plan(tag_map,plan):
        click.echo("valid plan applying")
        # os.system("terraform apply --var-file=keys.tfvars" + " -var ".join(tags) +" > apply.txt")
    else:
        click.echo("unexpected changes present , aborting apply")
    # os.system("rm plan.txt")

