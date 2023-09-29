from kafka import KafkaConsumer, KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from threading import Thread
import json
import time
import uuid

# Configuration for the kafka consumer
BOOTSTRAP_SERVERS =  'localhost:29092'
INSIGHTS_TOPIC = 'user-login-insights'

# Concurrency configurations
# This can be fine tuned by experimenting with various values
# to attain higher throughput and lower latencies
MAX_RECORDS = 10
THREAD_POOL_THREADS_COUNT = 10

# Insights dictionaries to store in-memory insights on user logins data
number_of_user_logins = 0
device_type_insights = {}
device_type_insights['android'] = 0
device_type_insights['iOS'] = 0
device_type_insights['NS'] = 0 # Not Specified
locale_insights = {}

# Initialize kafka consumer to user-login topic
consumer = KafkaConsumer('user-login', # Topic name to subscribe to
                         group_id='user-login-analytics', # Group name
                         bootstrap_servers=[BOOTSTRAP_SERVERS], # Connect to the bootstrap server
                         auto_offset_reset='earliest', # Start processing the logged messages from the start of the queue
                         enable_auto_commit=True # Enable auto offset commiting. By-default it is 5 seconds
                         )

# Poll batch of records from the Kafka consumer iterator and return the batch
def poll_records(consumer, max_records):
    num_records = 0
    messages = []

    for message in consumer:
        messages.append(message)
        num_records += 1
        if num_records == max_records:
            break

    return messages

# Initialize kafka producer to store user logins insights to user-login-insights topic
producer = KafkaProducer(bootstrap_servers=[BOOTSTRAP_SERVERS])

# Add new topic to the Kafka cluster
admin_client = KafkaAdminClient(bootstrap_servers=BOOTSTRAP_SERVERS)
if INSIGHTS_TOPIC not in admin_client.list_topics():
    topic = NewTopic(name=INSIGHTS_TOPIC, num_partitions=1, replication_factor=1)
    admin_client.create_topics(new_topics=[topic], validate_only=False)

# Function which decodes the records and processes the user logins
# to generate insights and store them to user-logins-insights topic
def process_logins(logins):
    for login in logins:
        global number_of_user_logins
        number_of_user_logins += 1
        login = login.value.decode('utf-8')
        login = json.loads(login)
        locale = login['locale']
        if 'device_type' in login:
            device_type = login['device_type']
        else:
            device_type = 'NS'

        if locale not in locale_insights:
            locale_insights[locale] = 0
        locale_insights[locale] += 1
        device_type_insights[device_type] += 1
        print(number_of_user_logins, locale_insights, device_type_insights)

        insights = {}
        insights['number_of_user_logins'] = number_of_user_logins
        insights['locale_insights'] = locale_insights
        insights['device_type_insights'] = device_type_insights
        insights['timestamp'] = int(time.time())

        producer.send(INSIGHTS_TOPIC, key=bytes(str(uuid.uuid4()), 'utf-8'), value=bytes(str(insights), 'utf-8'))
        producer.flush()

try:
    while True:
        num_threads_spawned = 0
        threads = [0] * THREAD_POOL_THREADS_COUNT
        # Spawn threads to process batch of user-login records from kafka consumer
        # This ensures parallelization of data processing and hence, increases the performance
        # and throughput of the data pipeline
        while num_threads_spawned < THREAD_POOL_THREADS_COUNT:
            logins = poll_records(consumer, 10)
            threads[num_threads_spawned] = Thread(target=process_logins, args=[logins])
            threads[num_threads_spawned].start()
            num_threads_spawned += 1

        # Wait for all the threads to complete before executing another batches of records
        thread_wait_index = 0
        while thread_wait_index < THREAD_POOL_THREADS_COUNT:
            threads[thread_wait_index].join()
            thread_wait_index += 1
except KeyboardInterrupt:
    pass

producer.flush(30)
producer.close()
