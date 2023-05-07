import boto3
import datetime
from boto3.dynamodb.conditions import Attr

TABLE_NAME = 'account'
ATTR_NAME_DATA_CREATED = 'dataCreatedAt'
ATTR_NAME_ID = 'id'
USER_POOL_ID = 'ap-northeast-1_KhuJtdjJ3'

dynamodb = boto3.resource('dynamodb')
cognito_client = boto3.client('cognito-idp')
ses_client = boto3.client('ses')
table = dynamodb.Table(TABLE_NAME)


def lambda_handler(event: dict, context: dict) -> dict:
    axis_utctime = datetime.datetime.utcnow()

    # alert
    alert_users = table.scan(
        FilterExpression=Attr(ATTR_NAME_DATA_CREATED).lt(
            calc_after_as_timestamp(axis_utctime, (5*365)-30))
    )

    for alert_user in alert_users['Items']:
        send_alert_email(alert_user['email'])

    # remove
    delete_users = table.scan(
        FilterExpression=Attr(ATTR_NAME_DATA_CREATED).lt(
            calc_after_as_timestamp(axis_utctime, 5*365))
    )

    for delete_user in delete_users['Items']:
        delete_cognito_user(delete_user[ATTR_NAME_ID])

    # disable
    disable_users = table.scan(
        FilterExpression=Attr(ATTR_NAME_DATA_CREATED).lt(
            calc_after_as_timestamp(axis_utctime, 3*365))
    )

    for disable_user in disable_users['Items']:
        disable_cognito_user(disable_user[ATTR_NAME_ID])

    return {
        "statusCode": 200,
        "body": "OK"
    }


def calc_after_as_timestamp(axis_utctime: datetime.datetime, days: int) -> int:
    three_years_ago = axis_utctime - datetime.timedelta(days=days)
    timestamp = int(three_years_ago.timestamp()/1000)
    return timestamp


def send_alert_email(email: str) -> None:
    # Send Email
    ses_client.send_email(
        Destination={
            'ToAddresses': [email]
        },
        Message={
            'Subject': {
                'Charset': 'utf-8',
                'Data': 'Notice: Account deletion alert'
            },
            'Body': {
                'Html': {
                    'Charset': 'utf-8',
                    'Data': 'This accounts may remove after 30 days'
                }
            }
        }
    )


def disable_cognito_user(user_id: str) -> None:
    cognito_client.admin_disable_user(
        UserPoolId=USER_POOL_ID,
        Username=user_id
    )


def delete_cognito_user(user_id: str) -> None:
    cognito_client.admin_delete_user(
        UserPoolId=USER_POOL_ID,
        Username=user_id
    )
