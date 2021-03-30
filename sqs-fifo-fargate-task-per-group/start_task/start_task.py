import boto3
import os
import json
import random
import traceback

ecs_client = boto3.client('ecs')
sqs_resource = boto3.resource('sqs')
sqs_client = boto3.client('sqs')
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

        queue_url = ''
        queue_name = f"TaskQueue_{group_id}.fifo"
        if len(tag_response['ResourceTagMappingList']) == 0:
            response_sqs = sqs_client.create_queue(
                QueueName=queue_name,
                Attributes={
                    'FifoQueue': 'true',
                    'ContentBasedDeduplication': 'true'
                }
            )
            queue_url = response_sqs['QueueUrl']
        else:
            response_sqs = sqs_client.get_queue_url(
                QueueName=queue_name
            )
            queue_url = response_sqs['QueueUrl']

        queue = sqs_resource.Queue(queue_url)

        request_body.update({
            'random': random.randint(0, 100)
        })
        queue.send_message(
            MessageBody=json.dumps(request_body),
            MessageGroupId=group_id
        )

        if len(tag_response['ResourceTagMappingList']) == 0:
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
            "body": json.dumps({'message': 'Task Iniciada com sucesso!!!'})
        }
    except Exception as e:
        traceback.print_exc()
        return {
            "statusCode": 400,
            "body": json.dumps({'error': str(e)})
        }
