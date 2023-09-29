# fetch-backend
Fetch-data: Home Assignment: Efficient Kafka Consumer implementation

## Setup
```
# Pull the repository to the local machine
$ git clone https://github.com/divy9881/fetch-data

# Change directory to the fetch-data
$ cd ./fetch-data

# Install pip(pip install packages) dependencies
$ pip install -r requirements.txt

# Build and run containers/services defined in compose.yaml
$ docker compose up

# Start Kafka Consumer Data Processing
$ python ./kafka-consumer.py
```

## File tree

- **app.js** - Kafka Consumer code to process the user logins data and generate insights from it
- **compose.yaml** - Definition of container services like Kafka Producer, Zookeeper as a control-plane, and Confluent-Kafka as a broker orchestrator
- **requirements.txt** - Used by pip to keep track of external dependencies
- **.gitignore** - To ignore python dependency directory and other beefy files, so as to not take up much git storage space

## Code implementation and design considerations for performance
- To introduce parallelism in consuming and processing user login records, I have created a pool of threads, where each thread can be pinned to a different CPU core to leverage the parallelism of isolation of cores.
- Each thread processes a batch of user login data records. A thread generates insights from the batch of records and pushes this insights to the user-logins-insights topic.
- The number of threads in a thread pool and the batch size can be fine tuned, by experimenting on various combinations, to increase the throughput and decrease the latency of the pipeline

## How would you deploy this application in production?
- Using docker compose, we can orchestrate various containers of services, and can be deployed to a cluster of nodes
- A fully-managed Enterprise Kafka Cloud provider like Confluent can be used to deploy our production-ready data pipeline

## What other components would you want to add to make this production ready?
- Consumer groups can be used to allow consuming data by multiple consumers subscribed to same topic. New consumers can be added on the fly to the group as the load of incoming data increases.
- Load balancer can be introduced to avoid hotspots in the consumer groups(i.e. a consumer node burdened with consuming a lot of data, while others are sitting idle)
- A external service which could constantly auto-tune consumer configurations like batch-sizes, auto offset committing intervals, number of threads in a thread pool to manage the concurrency
- Dynamic partition assignment can be done to automatically balance the partitions among consumer instances

## How can this application scale with a growing dataset?
- Multiple instances of consumers can be added to a consumer group, to increase the pace of consumption of data, and hence, to increase the throughput with increasing amount of incoming data
