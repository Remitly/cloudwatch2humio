import boto3
import os
import helpers

# Set environment variables.
humio_log_ingester_arn = os.environ["humio_log_ingester_arn"]
humio_subscription_prefix = os.environ.get("humio_subscription_prefix")
humio_subscription_tag_name = os.environ.get("humio_susbscription_tag_name")

# Set up CloudWatch Logs client.
log_client = boto3.client("logs")


def lambda_handler(event, context):
    """
    Subscribes log ingester to log group from event.

    :param event: Event data from CloudWatch Logs.
    :type event: dict

    :param context: Lambda context object.
    :type context: obj

    :return: None
    """
    # Grab the log group name from incoming event.
    log_group_name = event["detail"]["requestParameters"]["logGroupName"]
    log_group_tags = event["detail"]["requestParameters"]["tags"]
  
    # Check whether the prefix is set - the prefix is used to determine which logs we want.
    # Also check if there is a tag name specified - if the tag exists, then that filters logs as well.
    if not humio_subscription_prefix and not humio_subscription_tag_name:
        helpers.create_subscription(
            log_client, log_group_name, humio_log_ingester_arn, context
        )
    else:
        # Are we filtering based on a prefix? If so, then check that the log group name is prefixed correctly.
        matches_prefix = not humio_subscription_prefix or log_group_name.startswith(humio_subscription_prefix)

        # Are we filtering on tags? If so, check for the EXISTENCE ONLY of the given tag.
        has_tag_specified = not humio_subscription_tag_name or (humio_subscription_tag_name in log_group_tags.keys())

        if has_tag_specified and matches_prefix:
            helpers.create_subscription(
                log_client, log_group_name, humio_log_ingester_arn, context
            )
        else:
            helpers.delete_subscription(
                log_client, log_group_name, humio_log_ingester_arn, context
            )
