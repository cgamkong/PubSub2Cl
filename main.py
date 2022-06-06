import time
import json
from google.cloud import pubsub_v1
from concurrent.futures import TimeoutError
from google.cloud import logging

# Instantiates a client
logging_client = logging.Client()

# The name of the log to write to
log_name = "pubsub-log-cloud-run"
# Selects the log to write to
logger = logging_client.logger(log_name)

count = 1
def publish(message, retryCount):
    #Configuration
    project_id = "prj-dfobservability-s-14af"
    topic_id = "recoverable-errors"

    timestamp = str(int(time.time()))

    publisher_options = pubsub_v1.types.PublisherOptions(enable_message_ordering=True)
    publisher = pubsub_v1.PublisherClient(
        publisher_options=publisher_options
    )
    topic_path = publisher.topic_path(project_id, topic_id)

    try:
        global count
        if count == 4:
            # Writes the log entry
            logger.log_text("Bigquery Error")
            count = 0
        else:
            logger.log_text(str(message))
            count += 1
        # Add two attributes, origin and username, to the message
        future = publisher.publish(
            topic_path, data=message.data, messageId=timestamp, publishTime=timestamp, orderingKey=message.ordering_key, retryCount=str(retryCount)
        )
        print(f"Published messages with custom attributes to {topic_path}.")
    except Exception as e:
        print(e)
        retryCount += 1
        publish(message, retryCount)

def stream(request):
    # TODO(developer)
    project_id = "prj-dfobservability-s-14af"
    subscription_id = "cloudrunretryutility"
    # Number of seconds the subscriber should listen for messages
    timeout = 5.0
    subscriber = pubsub_v1.SubscriberClient()
    # The `subscription_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/subscriptions/{subscription_id}`
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    def callback(message: pubsub_v1.subscriber.message.Message) -> None:
        publish(message, 0)
        message.ack()

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}..\n")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber:
        try:
            # When `timeout` is not set, result() will block indefinitely,
            # unless an exception is encountered first.
            streaming_pull_future.result(timeout=timeout)
        except TimeoutError:
            streaming_pull_future.cancel()  # Trigger the shutdown.
            streaming_pull_future.result()  # Block until the shutdown is complete.

    return "Done"
