import boto3
import json

data = {
    "Resources": {
        "TestDynamoDB": {
            "Type": "AWS::DynamoDB::Table",
            "Properties": {
                "TableName": "test-table",
                "AttributeDefinitions": [
                    {
                        "AttributeName": "id",
                        "AttributeType": "S"
                    }
                ],
                "KeySchema": [
                    {
                        "AttributeName": "id",
                        "KeyType": "HASH"
                    }
                ],
                "BillingMode": "PAY_PER_REQUEST",
                "Tags": [
                    {
                        "Key": "Backup",
                        "Value": "Backup-test"
                    }
                ]
            }
        },
        "TestVault": {
            "Type": "AWS::Backup::BackupVault",
            "Properties": {
                "BackupVaultName": "test-vault"
            }
        },
        "TestPlan": {
            "Type": "AWS::Backup::BackupPlan",
            "Properties": {
                "BackupPlan": {
                    "BackupPlanName": "test-plan",
                    "BackupPlanRule": [
                        {
                            "RuleName": "test-rule",
                            "TargetBackupVault": {"Ref": "TestVault"},
                            "ScheduleExpression": "cron(25 11 ? * * *)",
                            "Lifecycle":
                            {
                                "DeleteAfterDays": 2
                            }
                        }
                    ]
                }
            },
            "DependsOn": "TestVault"
        },
        "TestSelection": {
            "Type": "AWS::Backup::BackupSelection",
            "Properties": {
                "BackupSelection": {
                    "SelectionName": "test-selection",
                    "IamRoleArn": {
                        "Fn::GetAtt": [
                            "TestSelectionRole",
                            "Arn"
                        ]
                    },
                    "ListOfTags": [
                        {
                            "ConditionType": "STRINGEQUALS",
                            "ConditionKey": "Backup",
                            "ConditionValue": "Backup-test"
                        }
                    ]
                },
                "BackupPlanId": {"Ref": "TestPlan"}
            },
            "DependsOn": [
                "TestPlan",
                "TestSelectionRole"
            ]
        },
        "TestSelectionRole": {
            "Type": "AWS::IAM::Role",
            "Properties": {
                "RoleName": "backup-test-role",
                "AssumeRolePolicyDocument": {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "backup.amazonaws.com"
                            },
                            "Action": [
                                "sts:AssumeRole"
                            ]
                        }
                    ]
                },
                "Path": "/",
                "Policies": [
                    {
                        "PolicyName": "backup-test-policy",
                        "PolicyDocument": {
                            "Version": "2012-10-17",
                            "Statement": [
                                {
                                    "Effect": "Allow",
                                    "Action": [
                                        "*"
                                    ],
                                    "Resource": "*"
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }
}

cf_cli = boto3.client("cloudformation")
res = cf_cli.update_stack(StackName="backup-test",
                          TemplateBody=json.dumps(data),
                          Capabilities=['CAPABILITY_NAMED_IAM'])
print(res)
