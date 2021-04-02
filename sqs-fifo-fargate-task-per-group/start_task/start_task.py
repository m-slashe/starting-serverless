import boto3
import os
import json
import random
import traceback

ecs_client = boto3.client('ecs')
sqs_resource = boto3.resource('sqs')
tag_client = boto3.client('resourcegroupstaggingapi')


def lambda_handler(event, context):
    try:
        request_body = json.loads(event['body'])

        tag_group_id_name = 'SQS_GROUP_ID'
        group_id = request_body['group_id']

        tag_response = tag_client.get_resources(
            TagFilters=[
                {'Key': tag_group_id_name, 'Values': [group_id]}
            ],
            ResourceTypeFilters=['ecs:task']
        )

        has_a_running_task = len(tag_response['ResourceTagMappingList']) == 0

        queue_url = os.environ['SQS_FIFO_URL']

        queue = sqs_resource.Queue(queue_url)

        request_body.update({
            'random': random.randint(0, 100)
        })
        queue.send_message(
            MessageBody=json.dumps(request_body),
            MessageGroupId=group_id
        )

        if has_a_running_task:
            ecs_client.run_task(
                cluster=os.environ['CLUSTER_TASK'],
                launchType='FARGATE',
                taskDefinition=os.environ['TASK_DEFINITION'],
                count=1,
                networkConfiguration={
                    'awsvpcConfiguration': {
                        'assignPublicIp': 'ENABLED',
                        'subnets': os.environ['SUBNETS'].split(','),
                        'securityGroups': os.environ['SECURITY_GROUPS'].split(',')
                    }
                },
                overrides={
                    'containerOverrides': [
                        {
                            'name': os.environ['CONTAINER_NAME'],
                            'environment': [
                                {'name': tag_group_id_name, 'value': group_id},
                                {'name': 'SQS_FIFO_URL', 'value': queue_url}
                            ]
                        }
                    ]
                },
                tags=[
                    {'key': tag_group_id_name, 'value': group_id}
                ]
            )

        return {
            "statusCode": 200,
            "body": json.dumps({'message': 'Task initialized with success!!!'})
        }
    except Exception as e:
        traceback.print_exc()
        return {
            "statusCode": 400,
            "body": json.dumps({'error': str(e)})
        }
