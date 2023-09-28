from kafka import KafkaConsumer

consumer = KafkaConsumer('user-login', # Topic name to subscribe to
                         group_id='user-login-analytics', # Group name
                         bootstrap_servers=['localhost:29092'], # Connect to the bootstrap server
                         auto_offset_reset='earliest', # Start processing the logged messages from the start of the queue
                         enable_auto_commit=True # Enable auto offset commiting. By-default it is 5 seconds
                         )

for message in consumer:
    print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                          message.offset, message.key,
                                          message.value))