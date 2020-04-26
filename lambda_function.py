import datetime
import json
import logging
import os
import re
import sys
import traceback

import boto3

conf = dict()
conf['log_level'] = os.environ.get('LOG_LEVEL', 'INFO')
conf['dynamodb_table_name'] = os.environ.get(
    'DYNAMODB_TABLE_NAME', 'dns-manager',
)

route53 = boto3.client('route53')
dynamodb = boto3.client('dynamodb')

# Apply logging configuration
log = logging.getLogger(__name__)
log.setLevel(conf['log_level'])
FORMAT = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(format=FORMAT)


def validate_event(event):
    '''Check if request has valid input and permissions to manage records.'''
    if isinstance(event['body'], str):
        event['body'] = json.loads(event['body'])
    print(json.dumps({'event': event}, default=str))
    data = event['body']
    if len(str(data)) > 512:
        #log.error('Input is to long')
        print(json.dumps({'message': 'Input is to long'}, default=str))
        sys.exit('Input is to long')
    try:
        json_test = json.dumps(data)
    except:
        #log.error('json from event["body"] is not valid')
        print(
            json.dumps(
                {'message': 'json from event["body"] is not valid'}, default=str,
            ),
        )
        sys.exit('json from event["body"] is not valid')
    validate_event_keys(data)
    validate_event_action(data)
    validate_event_username(data)
    validate_event_nameservers(data)
    validate_event_zoneid(data)
    validate_event_domainname(data)
    validate_event_email(data)


def validate_event_action(data):
    '''Check if request has valid Action key.'''
    # Action unknown
    if data.get('Action') not in ['CREATE', 'DELETE', 'UPDATE']:
        #log.error('Action is not valid')
        print(json.dumps({'message': 'Action is not valid'}, default=str))
        sys.exit('Action is not valid')


def validate_event_keys(data):
    '''Check if request has mandatory keys.'''
    # Not mandatory 'NameServers' handler for 'Action': 'DELETE'
    if data['Action'] == 'DELETE' and 'NameServers' not in data:
        data['NameServers'] = 'fake1,fake2'
    for key in ['Action', 'UserName', 'NameServers', 'ZoneID', 'DomainName', 'Email']:
        if key not in data:
           #log.error('Key: "{}" is not set'.format(key))
            print(
                json.dumps(
                    {'message': 'Key is not set', 'key': key}, default=str,
                ),
            )
            sys.exit('Key: "{}" is not set'.format(key))


def validate_event_username(data):
    '''Check if request has valid UserName key.'''
    key = 'UserName'
    regexp = re.match(r'^[0-9a-zA-Z\-_]+$', data[key])
    if not regexp:
        sys.exit('{} value is not valid: "{}"'.format(key, data[key]))


def validate_event_nameservers(data):
    '''Check if request has valid NameServers key.'''
    key = 'NameServers'
    regexp = re.match(r'^[0-9a-zA-Z\-\.,]+$', data[key])
    if not regexp:
        sys.exit('{} value is not valid: "{}"'.format(key, data[key]))


def validate_event_zoneid(data):
    '''Check if request has valid ZoneID key.'''
    key = 'ZoneID'
    regexp = re.match(r'^[0-9a-zA-Z]+$', data[key])
    if not regexp:
        sys.exit('{} value is not valid: "{}"'.format(key, data[key]))


def validate_event_domainname(data):
    '''Check if request has valid DomainName key.'''
    key = 'DomainName'
    regexp = re.match(r'^[0-9a-zA-Z\-\.]+$', data[key])
    if not regexp:
        sys.exit('{} value is not valid: "{}"'.format(key, data[key]))


def validate_event_email(data):
    '''Check if request has valid Email key.'''
    key = 'Email'
    regexp = re.match(r'^[0-9a-zA-Z\-\.@]+$', data[key])
    if not regexp:
        sys.exit('{} value is not valid: "{}"'.format(key, data[key]))


def data_from_event_to_config(event):
    '''Add data from "event" to dictionary with config options.'''
    for key in event['body']:
        value = event['body'][key]
        conf[key] = value
    if not conf['DomainName'].endswith('.'):
        conf['DomainName'] += '.'
    conf['NameServers_list'] = conf['NameServers'].split(',')
    for index in range(len(conf['NameServers_list'])):
        ns = conf['NameServers_list'][index]
        if not ns.endswith('.'):
            conf['NameServers_list'][index] += '.'
    conf['source_ip'] = event['headers']['X-Forwarded-For']
    #log.debug('Config content: {}'.format(conf))
    print(json.dumps(conf, default=str))


def check_if_request_authorized():
    '''Check if request has valid input and permissions to manage records.'''
    if not conf['dynamodb_record']:
        return
    provided_id = conf['ID']
    current_id = conf['dynamodb_record']['ID']['S']
    provided_password = conf['ZoneID']
    current_password = conf['dynamodb_record']['ZoneID']['S']
    if provided_id == current_id:
        if provided_password != current_password:
            sys.exit('Wrong password to change record')


def get_zone_id_from_route53():
    '''Get zone id in route53 for main domain (DomainName).'''
    zone = route53.list_hosted_zones_by_name(
        DNSName=conf['DomainName'], MaxItems='1',
    )['HostedZones'][0]
    # log.debug(
    #    'Got zone id - Domain in request: "{}" | Domain in response: "{}" | Zone Id in response: "{}" '.format(
    #        conf['DomainName'],
    #        zone['Name'],
    #        zone['Id']
    #    )
    # )
    print(
        json.dumps(
            {
                'message': 'Got zone id',
                'Domain in request': conf['DomainName'],
                'Domain in response': zone['Name'],
                'Zone Id in response': zone['Id'],
            },
            default=str,
        ),
    )
    conf['DomainNameId'] = zone['Id'].split('/')[-1]


def get_record_from_route53():
    '''Get target record from route53 zone.'''
    conf['record_name'] = '{}.{}'.format(conf['UserName'], conf['DomainName'])
    #log.debug('Getting record from route53 zone - Record in request: "{}"'.format(conf['record_name']))
    print(
        json.dumps(
            {
                'message': 'Getting record from route53 zone',
                'request': {
                    'HostedZoneId': conf['DomainNameId'],
                    'StartRecordName': conf['record_name'],
                    'StartRecordType': 'NS',
                    'MaxItems': 1,
                },
            },
            default=str,
        ),
    )
    response = route53.list_resource_record_sets(
        HostedZoneId=conf['DomainNameId'],
        StartRecordName=conf['record_name'],
        StartRecordType='NS',
        MaxItems='1',
    )
    #log.debug('Getting record from route53 zone - Response: "{}"'.format(response))
    print(
        json.dumps(
            {
                'message': 'Getting record from route53 zone',
                'response': response,
            },
            default=str,
        ),
    )
    if response['ResourceRecordSets']:
        record_name = response['ResourceRecordSets'][0]['Name']
        record_type = response['ResourceRecordSets'][0]['Type']
    else:
        conf['route53_record'] = False
        return
    if record_name == conf['record_name'] and record_type == 'NS':
        conf['route53_record'] = response['ResourceRecordSets'][0]['ResourceRecords']
    else:
        conf['route53_record'] = False


def create_record_in_route53():
    '''Create target record in route53 zone.'''
    records = list()
    for ns in conf['NameServers_list']:
        record = {'Value': ns}
        records.append(record)
    data = {
        'Comment': 'Managed by "dns-manager" lambda function',
        'Changes': [
            {
                'Action': 'CREATE',
                'ResourceRecordSet': {
                    'Name': conf['record_name'],
                    'Type': 'NS',
                    'TTL': 60,
                    'ResourceRecords': records,
                },
            },
        ],
    }
    #log.debug('Creating record in route53 zone - Request: "{}"'.format(data))
    print(
        json.dumps(
            {
                'message': 'Creating record in route53 zone',
                'request': data,
            },
            default=str,
        ),
    )
    response = route53.change_resource_record_sets(
        HostedZoneId=conf['DomainNameId'],
        ChangeBatch=data,
    )
    #log.debug('Creating record in route53 zone - Response: "{}"'.format(response))
    #log.debug('Creating record in route53 zone - Record: "{}" added'.format(conf['record_name']))
    print(
        json.dumps(
            {
                'message': 'Creating record in route53 zone',
                'response': response,
            },
            default=str,
        ),
    )
    print(
        json.dumps(
            {
                'message': 'Record added',
                'record': conf['record_name'],
            },
            default=str,
        ),
    )


def delete_record_in_route53():
    '''Delete target record in route53 zone.'''
    data = {
        'Comment': 'Created by dns-manager lambda',
        'Changes': [
            {
                'Action': 'DELETE',
                'ResourceRecordSet': {
                    'Name': conf['record_name'],
                    'Type': 'NS',
                    'TTL': 60,
                    'ResourceRecords': conf['route53_record'],
                },
            },
        ],
    }
    #log.debug('Deleting record in route53 zone - Request: "{}"'.format(data))
    print(
        json.dumps(
            {
                'message': 'Deleting record in route53 zone',
                'request': data,
            },
            default=str,
        ),
    )
    response = route53.change_resource_record_sets(
        HostedZoneId=conf['DomainNameId'],
        ChangeBatch=data,
    )
    #log.debug('Deleting record in route53 zone - Response: "{}"'.format(response))
    #log.debug('Deleting record in route53 zone - Record: "{}" deleted'.format(conf['record_name']))
    print(
        json.dumps(
            {
                'message': 'Deleting record in route53 zone',
                'response': response,
            },
            default=str,
        ),
    )
    print(
        json.dumps(
            {
                'message': 'Record deleted',
                'record': conf['record_name'],
            },
            default=str,
        ),
    )


def update_record_in_route53():
    '''Update target record in route53 zone.'''
    records = list()
    for ns in conf['NameServers_list']:
        record = {'Value': ns}
        records.append(record)
    data = {
        'Comment': 'Managed by "dns-manager" lambda function',
        'Changes': [
            {
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': conf['record_name'],
                    'Type': 'NS',
                    'TTL': 60,
                    'ResourceRecords': records,
                },
            },
        ],
    }
   #log.debug('Updating record in route53 zone - Request: "{}"'.format(data))
    print(
        json.dumps(
            {
                'message': 'Updating record in route53 zone',
                'request': data,
            },
            default=str,
        ),
    )
    response = route53.change_resource_record_sets(
        HostedZoneId=conf['DomainNameId'],
        ChangeBatch=data,
    )
    #log.debug('Updating record in route53 zone - Response: "{}"'.format(response))
    #log.debug('Updating record in route53 zone - Record: "{}" updated'.format(conf['record_name']))
    print(
        json.dumps(
            {
                'message': 'Updating record in route53 zone',
                'response': response,
            },
            default=str,
        ),
    )
    print(
        json.dumps(
            {
                'message': 'Record updated',
                'record': conf['record_name'],
            },
            default=str,
        ),
    )


def get_item_from_dynamodb():
    '''Get item from DynamoDB table.'''
    conf['ID'] = '{}_{}'.format(
        conf['UserName'],
        conf['DomainName'],
        # conf['ZoneID'],
        # conf['Email']
    )
    data = {
        'ID': {
            'S': conf['ID'],
        },
    }
    response = dynamodb.get_item(
        TableName=conf['dynamodb_table_name'],
        Key=data,
    )
   #log.debug('Getting item from DynamoDB - Response: "{}"'.format(response))
    print(
        json.dumps(
            {
                'message': 'Getting item from DynamoDB',
                'id': conf['ID'],
                'key': data,
            },
            default=str,
        ),
    )
    print(
        json.dumps(
            {
                'message': 'Getting item from DynamoDB',
                'response': response,
            },
            default=str,
        ),
    )
    conf['dynamodb_record'] = response.get('Item')


def add_item_to_dynamodb():
    '''Add item to DynamoDB table.'''
    last_update_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    data = {
        'ID': {
            'S': conf['ID'],
        },
        'UserName': {'S': conf['UserName']},
        'DomainName': {'S': conf['DomainName']},
        'ZoneID': {'S': conf['ZoneID']},
        'NameServers': {'S': conf['NameServers']},
        'Email': {'S': conf['Email']},
        'LastUpdateUTC': {'S': last_update_time},
        'SourceIP': {'S': conf['source_ip']},
    }
    response = dynamodb.put_item(
        TableName=conf['dynamodb_table_name'],
        Item=data,
    )
   #log.debug('Adding item to DynamoDB - Response: "{}"'.format(response))
    print(
        json.dumps(
            {
                'message': 'Adding item to DynamoDB',
                'response': response,
            },
            default=str,
        ),
    )
    conf['response'] = 'CREATE OK'


def update_item_in_dynamodb():
    '''Update item in DynamoDB table.'''
    last_update_time = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    data = {
        'ID': {
            'S': conf['ID'],
        },
        'UserName': {'S': conf['UserName']},
        'DomainName': {'S': conf['DomainName']},
        'ZoneID': {'S': conf['ZoneID']},
        'NameServers': {'S': conf['NameServers']},
        'Email': {'S': conf['Email']},
        'LastUpdateUTC': {'S': last_update_time},
        'SourceIP': {'S': conf['source_ip']},
    }
    response = dynamodb.put_item(
        TableName=conf['dynamodb_table_name'],
        Item=data,
    )
   #log.debug('Updating item in DynamoDB - Response: "{}"'.format(response))
    print(
        json.dumps(
            {
                'message': 'Updating item in DynamoDB',
                'response': response,
            },
            default=str,
        ),
    )
    conf['response'] = 'Update OK'


def delete_item_from_dynamodb():
    '''Delete item from DynamoDB table.'''
    data = {
        'ID': {
            'S': conf['ID'],
        },
    }
    response = dynamodb.delete_item(
        TableName=conf['dynamodb_table_name'],
        Key=data,
    )
   #log.debug('Deleting item from DynamoDB - Response: "{}"'.format(response))
    print(
        json.dumps(
            {
                'message': 'Deleting item from DynamoDB',
                'response': response,
            },
            default=str,
        ),
    )
    conf['response'] = 'Delete OK'


def action_create():
    '''Function to create new record.'''
    if not conf['dynamodb_record']:
        add_item_to_dynamodb()
        if not conf['route53_record']:
            create_record_in_route53()
        else:
           #log.debug('Record: "{}" exists already, nothing to add'.format(conf['record_name']))
            print(
                json.dumps(
                    {
                        'message': 'Record exists already, nothing to add',
                        'record': conf['record_name'],
                    },
                    default=str,
                ),
            )
            conf['response'] = 'Exists already'
    else:
       #log.debug('Item with ID: "{}" exists already, nothing to add'.format(conf['ID']))
        print(
            json.dumps(
                {
                    'message': 'Item exists already, nothing to add',
                    'id': conf['ID'],
                },
                default=str,
            ),
        )
        conf['response'] = 'Exists already'


def action_delete():
    '''Function to delete record.'''
    if conf['dynamodb_record']:
        delete_item_from_dynamodb()
        if conf['route53_record']:
            delete_record_in_route53()
        else:
           #log.debug('Record: "{}" not exists, nothing to delete'.format(conf['record_name']))
            print(
                json.dumps(
                    {
                        'message': 'Record not exists, nothing to delete',
                        'record': conf['record_name'],
                    },
                    default=str,
                ),
            )
            conf['response'] = 'Not exists'
    else:
       #log.debug('Item with ID: "{}" not exists, nothing to delete'.format(conf['ID']))
        print(
            json.dumps(
                {
                    'message': 'Item not exists, nothing to delete',
                    'id': conf['ID'],
                },
                default=str,
            ),
        )
        conf['response'] = 'Not exists'


def action_update():
    '''Function to update record.'''
    update_item_in_dynamodb()
    update_record_in_route53()
   # if conf['dynamodb_record']:
   #    update_item_in_dynamodb()
   #    if conf['route53_record']:
   #        update_record_in_route53()
   #    else:
   #       #log.debug('Record: "{}" not exists, nothing to update'.format(conf['record_name']))
   #        print(
   #            json.dumps(
   #                {
   #                    'message': 'Record not exists, nothing to update',
   #                    'record': conf['record_name']
   #                },
   #                default=str
   #            )
   #        )
   #        conf['response'] = 'Not exists'
   # else:
   #   #log.debug('Item with ID: "{}" not exists, nothing to update'.format(conf['ID']))
   #    print(
   #        json.dumps(
   #            {
   #                'message': 'Item not exists, nothing to update',
   #                'id': conf['ID']
   #            },
   #            default=str
   #        )
   #    )
   #    conf['response'] = 'Not exists'


def response():
    '''Return http response.'''
    response = '{{"Message": "{}"}}'.format(conf['response'])
    return {
        'statusCode': 200,
        'body': response,
    }


def lambda_handler(event, context):
    '''Main function, which starts first and contains all logic.'''
    try:
        validate_event(event)
        data_from_event_to_config(event)
        get_item_from_dynamodb()
        check_if_request_authorized()
        get_zone_id_from_route53()
        get_record_from_route53()
        if conf['Action'] == 'CREATE':
            action_update()
           # action_create()
        elif conf['Action'] == 'DELETE':
            action_delete()
        elif conf['Action'] == 'UPDATE':
            action_update()
        return response()
    except:
        trace = traceback.format_exception(
            sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2],
        )
       # log.critical(trace)
        print(
            json.dumps(
                {
                    'message': 'Exception',
                    'trace': trace,
                },
                default=str,
            ),
        )
       # log.info(conf)
        print(json.dumps(conf, default=str))
        conf['response'] = 'ERROR'
        return response()


# Execute only if run as a script, example:
# python3 dns-manager.py CREATE
if __name__ == "__main__":
    with open('./lambda_function.json') as json_file:
        test_event = json.load(json_file)
    test_event['body']['Action'] = sys.argv[1]
    print(lambda_handler(test_event, None))
