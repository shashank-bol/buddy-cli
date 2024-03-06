import click
import boto3
import json
import subprocess
aws_directory = ""
def run(mode , env , profile):
    if env is None:
        click.echo("Please enter env")
        return
    else:
        env = env.upper()
    if mode is None:
        click.echo("Please enter a mode")
        return
    if profile is None:
        click.echo("Enter a Profile name")
        return
    try:
        credentials = profile.strip()
        selection = mode.upper()
        session = boto3.Session(profile_name=credentials)
        client = session.client('secretsmanager', region_name='us-west-2')
        response = client.get_secret_value(SecretId='arn:aws:secretsmanager:us-west-2:975910769154:secret:sshuttle_details-NVpN3j',
            VersionStage='AWSCURRENT')
        loaded_data = response['SecretString']
        data = json.loads(loaded_data)
        version = str(data['version'])
        data = data[str(env.get()).strip().lower()]
        hello = "Connecting to " + env
        click.echo(hello)
        try:
            if selection == 'DB':
                out = subprocess.call(['kill $(lsof -t -i :2345) >/dev/null 2>&1'], shell=True)
                out = subprocess.call(['kill $(lsof -t -i :9736) >/dev/null 2>&1'], shell=True)
                out = subprocess.call(['kill $(lsof -t -i :8843) >/dev/null 2>&1'], shell=True)
                click.echo("Cleared Ports")
                return_code = subprocess.call([aws_directory + 'aws ec2-instance-connect send-ssh-public-key \
                          --instance-id {0} \
                          --availability-zone {1} \
                          --instance-os-user ec2-user \
                          --ssh-public-key file://~/.ssh/id_rsa.pub \
                          --profile {2} --region {3}'.format(data['db']['bastion_instance_id'], data['db']['az'], str(profile.get()).strip(), data['db']['region'])],
                shell=True)

                if return_code != 0:
                    return click.echo("Error")

                return_code = subprocess.call(['ssh -i ~/.ssh/id_rsa \
                          -Nf -M \
                          -L 2345:{0} \
                          -L 9736:{2} \
                          -L 8843:{6} \
                          -o "UserKnownHostsFile=/dev/null" \
                          -o "StrictHostKeyChecking=no" \
                          -o ProxyCommand="{7}aws ssm start-session --target %h --document AWS-StartSSHSession --parameters portNumber=%p --region={3} --profile={4}" \
                          ec2-user@{5}'.format(data['db']['rds'], data['db']['redshift'], data['db']['redis'],
                                               data['db']['region'], str(profile.get()).strip(), data['db']['bastion_instance_id'],
                                               data['db']['engine_url'], aws_directory)],
                shell=True)

                if return_code != 0:
                    return click.echo("Error")

            elif selection == 'EC2':
                return_code = subprocess.call([aws_directory + 'aws ssm start-session --target {0} --profile={1} --region={2}'.format(
                    data['ec2']['ecs_ec2_instance_id'], str(profile.get()).strip(), data['db']['region'])], shell=True)

                if return_code != 0:
                    return click.echo("Error")

            elif selection == 'ECS':
                if 'ecs' not in data:
                    return click.echo('Webapp is still not configured for {0}'.format(env))
                else:
                    cluster_id = data['ecs']['cluster_id']
                    ecs = session.client('ecs', region_name=data['db']['region'])
                    response = ecs.list_tasks(
                        cluster=cluster_id,
                        serviceName='webapp-mainV2-' + str(env.get()).strip().lower(),
                        desiredStatus='RUNNING',
                    )
                    taskId = response['taskArns'][0].split('/')[-1]
                    response = ecs.list_task_definitions(
                        familyPrefix='webapp-mainV2-' + str(env.get()).strip().lower(),
                        status='ACTIVE',
                        sort='DESC'
                    )
                    response1 = ecs.describe_task_definition(
                        taskDefinition=response['taskDefinitionArns'][0]
                    )
                    container_Def = response1['taskDefinition']['containerDefinitions']
                    for con_def in container_Def:
                        if con_def['name'] == 'webapp-main':
                            click.echo('Connecting to Webapp container running version ' +
                                con_def['image'].split(':')[1] + " ......")
                            break
                    return_code = subprocess.call([aws_directory + 'aws ecs execute-command  \
                                                                                            --region {0} \
                                                                                            --cluster {1} \
                                                                                            --task {2} \
                                                                                            --profile {3} \
                                                                                            --container webapp-main \
                                                                                            --command "/bin/bash" \
                                                                                            --interactive'.format(
                                data['db']['region'], cluster_id, taskId,profile)], shell=True)

                    if return_code != 0:
                        return click.echo("Error")

            elif selection == 'REDSHIFT':
                        try:
                            if len(data['db']['redshift']) == 0:
                                return click.echo("No redshift")

                            try:
                                out = subprocess.call(['kill $(lsof -t -i :5439) >/dev/null 2>&1'], shell=True)
                                click.echo("Cleared Ports")

                                return_code = subprocess.call([aws_directory + 'aws ec2-instance-connect send-ssh-public-key \
                                  --instance-id {0} \
                                  --availability-zone {1} \
                                  --instance-os-user ec2-user \
                                  --ssh-public-key file://~/.ssh/id_rsa.pub \
                                  --profile {2} --region {3}'.format(data['db']['bastion_instance_id'], data['db']['az'],
                                                                     profile, data['db']['region'])],
                                                              shell=True)

                                if return_code != 0:
                                    return click.echo("Error")

                                return_code = subprocess.call(['ssh -i ~/.ssh/id_rsa \
                                  -Nf -M \
                                  -L 5439:{0} \
                                  -o "UserKnownHostsFile=/dev/null" \
                                  -o "StrictHostKeyChecking=no" \
                                  -o ProxyCommand="{4}aws ssm start-session --target %h --document AWS-StartSSHSession --parameters portNumber=%p --region={1} --profile={2}" \
                                  ec2-user@{3}'.format(data['db']['redshift'], data['db']['region'],
                                                       profile, data['db']['bastion_instance_id'],
                                                       aws_directory)],
                                                       shell=True)

                                if return_code != 0:
                                    return click.echo("Error")

                                click.echo("Connected to " + env + "redshift" )

                            except:
                                return click.echo("Error")

                        except:
                            return click.echo("Error")

            elif selection == 'DATALAKE':
                        try:
                            if len(data['ec2']['datalake_instance_id']) == 0:
                                return click.echo("Error")

                            try:

                                out = subprocess.call(['kill $(lsof -t -i :9154) >/dev/null 2>&1'], shell=True)
                                click.echo("Cleared Ports")

                                return_code = subprocess.call([aws_directory + 'aws ec2-instance-connect send-ssh-public-key \
                                  --instance-id {0} \
                                  --availability-zone {1} \
                                  --instance-os-user ec2-user \
                                  --ssh-public-key file://~/.ssh/id_rsa.pub \
                                  --profile {2} --region {3}'.format(data['db']['bastion_instance_id'], data['db']['az'], profile, data['db']['region'])],
                                                shell=True)

                                if return_code != 0:
                                    return click.echo("Error")

                                return_code = subprocess.call(['ssh -i ~/.ssh/id_rsa \
                                  -Nf -M \
                                  -L 9154:{0} \
                                  -o "UserKnownHostsFile=/dev/null" \
                                  -o "StrictHostKeyChecking=no" \
                                  -o ProxyCommand="{4}aws ssm start-session --target %h --document AWS-StartSSHSession --parameters portNumber=%p --region={1} --profile={2}" \
                                  ec2-user@{3}'.format(data['ec2']['airflow_dns'], data['db']['region'],
                                                       str(profile.get()).strip(), data['db']['bastion_instance_id'],
                                                       aws_directory)],
                                                shell=True)

                                if return_code != 0:
                                    return click.echo("Error")

                                click.echo("coneected to " + env + " datalake")

                                return_code = subprocess.call([aws_directory + 'aws ssm start-session --target {0} --profile={1} --region={2}'.format(
                                    data['ec2']['datalake_instance_id'], str(profile.get()).strip(), data['db']['region'])], shell=True)

                                if return_code != 0:
                                    return click.echo("Error")

                            except:
                                return click.echo("Error")

                        except:
                            return click.echo("Error")

            elif selection == 'FLOWER':
                        out = subprocess.call(['kill $(lsof -t -i :5595) >/dev/null 2>&1'], shell=True)

                        try:
                            celery_task_ip = click.prompt("enter celery task ip for " + env + " :")
                            socket.inet_aton(celery_task_ip)
                        except:
                            return click.echo("Incorrect IP")

                        return_code = subprocess.call([aws_directory + 'aws ec2-instance-connect send-ssh-public-key \
                          --instance-id {0} \
                          --availability-zone {1} \
                          --instance-os-user ec2-user \
                          --ssh-public-key file://~/.ssh/id_rsa.pub \
                          --profile {2} --region {3}'.format(data['db']['bastion_instance_id'], data['db']['az'],
                                                             profile,data['db']['region'])],
                                                      shell=True)

                        if return_code != 0:
                            return click.echo("Error")

                        return_code = subprocess.call(['ssh -i ~/.ssh/id_rsa \
                          -Nf -M \
                          -L 5595:{0}:5555 \
                          -o "UserKnownHostsFile=/dev/null" \
                          -o "StrictHostKeyChecking=no" \
                          -o ProxyCommand="{4}aws ssm start-session --target %h --document AWS-StartSSHSession --parameters portNumber=%p --region={1} --profile={2}" \
                          ec2-user@{3}'.format(celery_task_ip,
                                               data['db']['region'],
                                               profile,
                                               data['db']['bastion_instance_id'],
                                               aws_directory)],shell=True)

                        if return_code != 0:
                            return click.echo("Error")

                        click.echo("connected to " + env + " flower")

            elif selection == 'COUCHBASE':
                        out = subprocess.call(['kill $(lsof -t -i :2347) >/dev/null 2>&1'], shell=True)
                        out = subprocess.call(['kill $(lsof -t -i :2348) >/dev/null 2>&1'], shell=True)
                        click.echo(text="Cleared Ports")

                        return_code = subprocess.call(['aws ec2-instance-connect send-ssh-public-key \
                                                  --instance-id {0} \
                                                  --availability-zone {1} \
                                                  --instance-os-user ec2-user \
                                                  --ssh-public-key file://~/.ssh/id_rsa.pub \
                                                  --profile {2} --region {3}'.format(data['db']['bastion_instance_id'],
                                                                                     data['db']['az'],
                                                                                     str(profile.get()).strip(),
                                                                                     data['db']['region'])],
                                                      shell=True)

                        if return_code != 0:
                            return click.echo("Error")

                        return_code = subprocess.call(['ssh -i ~/.ssh/id_rsa \
                                                  -Nf -M \
                                                  -L 2347:{0}:8091 \
                                                  -L 2348:{1}:8091 \
                                                  -o "UserKnownHostsFile=/dev/null" \
                                                  -o "StrictHostKeyChecking=no" \
                                                  -o ProxyCommand="aws ssm start-session --target %h --document AWS-StartSSHSession --parameters portNumber=%p --region={2} --profile={3}" \
                                                  ec2-user@{4}'.format(data['ec2']['hudi_master_instance_id'],
                                                                       data['ec2']['couch2'],
                                                                       data['db']['region'], str(profile.get()).strip(),
                                                                       data['db']['bastion_instance_id'],
                                                                       data['db']['engine_url'],
                                                                       aws_directory)],
                                                      shell=True)

                        if return_code != 0:
                            return click.echo("Error")

                        click.echo("connected to couchbase")

            elif selection == 'TOKEN':
                        print("\nRead Only Token -\n")
                        print("Username - {0}readonly\n".format(str(env.get()).strip().lower()))
                        return_code = subprocess.call([aws_directory + 'aws rds generate-db-auth-token --hostname {0} --port {1} \
                        --region {2} --username {3}readonly \
                        --profile {4}'.format(data['db']['rds'][:-5], data['db']['rds'][-4:],
                                              data['db']['az'][:-1],
                                              env.lower(),
                                              credentials)], shell=True)

                        if return_code != 0:
                            return click.echo("Error")

                        print("\nWrite Access Token -\n")
                        print("Username - {0}user\n".format(str(env.get()).strip().lower()))
                        return_code = subprocess.call([aws_directory + 'aws rds generate-db-auth-token --hostname {0} --port {1} \
                        --region {2} --username {3}user \
                        --profile {4}'.format(data['db']['rds'][:-5], data['db']['rds'][-4:],
                                              data['db']['az'][:-1],
                                              env.lower(),
                                              credentials)], shell=True)


                        if return_code != 0:
                            return click.echo("Error")

                        click.echo("generated token")

                    #############

            #     except:
            #         msg.config(text="Error", font='Helvetica', bg='#FF605C', fg='Black')
        except:
                label.config(text="Enter a valid ENV")
                env.delete(0, 'end')
    except:
        return click.echo("Credntial profile was not found")


def close():
    out = subprocess.call(['kill $(lsof -t -i :2345) >/dev/null 2>&1'], shell=True)
    out = subprocess.call(['kill $(lsof -t -i :5439) >/dev/null 2>&1'], shell=True)
    out = subprocess.call(['kill $(lsof -t -i :9736) >/dev/null 2>&1'], shell=True)
    out = subprocess.call(['kill $(lsof -t -i :8843) >/dev/null 2>&1'], shell=True)
    out = subprocess.call(['kill $(lsof -t -i :9154) >/dev/null 2>&1'], shell=True)
    out = subprocess.call(['kill $(lsof -t -i :5595) >/dev/null 2>&1'], shell=True)
    print('Goodbye :)')
    root.destroy()
