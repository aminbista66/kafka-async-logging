# kafka-async-logging

An asynchronous, event-driven logging system built on Apache Kafka. Application events are published to a Kafka topic by an HTTP API, buffered in Redis by a dedicated consumer, and periodically committed in batches to MongoDB by a scheduler service. This decouples request handling from log persistence, keeping API latency independent of database write throughput.

## Table of Contents

- [Architecture](#architecture)
- [Components](#components)
- [Data Flow](#data-flow)
- [Repository Structure](#repository-structure)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Local Development](#local-development)
- [Deployment](#deployment)
- [API Reference](#api-reference)
- [Known Limitations](#known-limitations)
- [License](#license)

## Architecture

```mermaid
flowchart LR
    Client([Client])

    subgraph K8s["Kubernetes Cluster"]
        Ingress[Ingress]
        Svc[Service<br/>NodePort 30007]
        API[API Server<br/>FastAPI x3 replicas]
    end

    Kafka[(Apache Kafka<br/>Confluent Cloud<br/>log_topic)]
    Consumer[Log Consumer]
    Redis[(Redis<br/>key: logs)]
    Scheduler[Scheduler<br/>APScheduler, 60s interval]
    Mongo[(MongoDB<br/>log_db.logs)]

    Client --> Ingress --> Svc --> API
    API -- produce --> Kafka
    Kafka -- consume --> Consumer
    Consumer -- buffer --> Redis
    Scheduler -- read and clear --> Redis
    Scheduler -- insert_many --> Mongo
    API -- query --> Mongo
```

## Components

| Component | Path | Technology | Responsibility |
|-----------|------|------------|----------------|
| API Server | `api/` | FastAPI, confluent-kafka | Accepts action events over HTTP and publishes them to Kafka; exposes stored logs from MongoDB. |
| Log Consumer | `log_consumer/` | confluent-kafka, redis-py | Subscribes to the log topic and appends each event to a JSON array held in Redis. |
| Scheduler | `scheduler/` | FastAPI, APScheduler, pymongo | Every 60 seconds, moves buffered logs from Redis into MongoDB and clears the buffer. |
| Data Stores | `redis/` | Docker Compose | Local MongoDB instance for development. |

## Data Flow

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant A as API Server
    participant K as Kafka
    participant LC as Log Consumer
    participant R as Redis
    participant S as Scheduler
    participant M as MongoDB

    C->>A: GET /action/{action_code}/
    A->>A: Build payload and assign event_id (UUID4)
    A->>K: produce(key=event_id, value=payload)
    A-->>C: 200 OK {data: payload}
    K-->>A: Delivery callback (logged to callback.log)

    LC->>K: poll()
    K-->>LC: Message
    LC->>K: commit offset (synchronous)
    LC->>R: GET logs, append event, SET logs (TTL 300s)

    loop Every 60 seconds
        S->>R: GET logs
        alt Buffer is not empty
            S->>M: insert_many(logs)
            S->>R: DEL logs
        end
    end

    C->>A: GET /get-logs
    A->>M: find()
    M-->>A: Documents
    A-->>C: 200 OK [logs]
```

### Event Schema

Each event published to Kafka and persisted to MongoDB has the following structure:

```json
{
  "action": "string",
  "created_at": "YYYY-MM-DD HH:MM:SS.ffffff",
  "event_id": "uuid4"
}
```

## Repository Structure

```
.
├── api/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── k8s/
│   │   ├── configmap.yml
│   │   ├── deployment.yml
│   │   ├── ingress.yml
│   │   └── service.yml
│   └── src/
│       ├── config.py        # Environment loading
│       ├── connector.py     # MongoDB client
│       ├── main.py          # FastAPI application
│       └── producer.py      # Kafka producer
├── log_consumer/
│   ├── consumer.py          # Kafka consumer and Redis buffer
│   ├── main.py              # Entry point
│   └── requirements.txt
├── scheduler/
│   ├── config.py            # Environment loading
│   ├── connectors.py        # MongoDB and Redis clients
│   ├── main.py              # FastAPI application
│   └── scheduler.py         # Periodic Redis-to-MongoDB commit job
├── redis/
│   └── docker-compose.yml   # Local MongoDB
└── LICENSE
```

## Prerequisites

- Python 3.10 or later
- Docker and Docker Compose
- A Kafka cluster with SASL/PLAIN over SSL (the project is configured for Confluent Cloud)
- A Redis instance
- A MongoDB instance
- `kubectl` and access to a Kubernetes cluster (for deployment only)

## Configuration

All services read configuration from environment variables. For local development, each service loads a `.env` file via `python-dotenv`.

| Variable | Used By | Default | Description |
|----------|---------|---------|-------------|
| `KAFKA_CLUSTER_SERVER` | API, Consumer | None | Kafka bootstrap server address (`host:port`). |
| `KAFKA_CLUSTER_USERNAME` | API, Consumer | None | SASL username (Confluent API key). |
| `KAFKA_CLUSTER_SECRET` | API, Consumer | None | SASL password (Confluent API secret). |
| `KAFKA_TOPIC_NAME` | API, Consumer | None (required) | Topic to which log events are published. |
| `KAFKA_CONSUMER_GUID` | Consumer | None | Kafka consumer group ID. |
| `REDIS_HOST` | Consumer, Scheduler | `localhost` | Redis hostname. |
| `REDIS_PORT` | Consumer, Scheduler | `6379` | Redis port. |
| `MONGO_URI` | API, Scheduler | None | MongoDB connection string. |

Example `.env`:

```dotenv
KAFKA_CLUSTER_SERVER=<bootstrap-server>:9092
KAFKA_CLUSTER_USERNAME=<api-key>
KAFKA_CLUSTER_SECRET=<api-secret>
KAFKA_TOPIC_NAME=log_topic
KAFKA_CONSUMER_GUID=log-consumer-group
REDIS_HOST=localhost
REDIS_PORT=6379
MONGO_URI=mongodb://root:example@localhost:27017
```

## Local Development

### 1. Start the data stores

Start MongoDB using the provided Compose file, and run Redis separately:

```bash
docker compose -f redis/docker-compose.yml up -d
docker run -d --name redis -p 6379:6379 redis:latest
```

### 2. Run the API server

```bash
cd api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt pymongo
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Run the log consumer

```bash
cd log_consumer
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt redis
python main.py
```

### 4. Run the scheduler

```bash
cd scheduler
python -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn apscheduler pymongo redis python-dotenv
uvicorn main:app --port 8001
```

### 5. Verify

```bash
curl http://localhost:8000/ping
curl http://localhost:8000/action/user_login/
# Wait up to 60 seconds for the scheduler to commit the batch
curl http://localhost:8000/get-logs
```

## Deployment

The API server is packaged as a container image and deployed to Kubernetes. Manifests are located in `api/k8s/`.

```mermaid
flowchart TB
    Ingress["Ingress<br/>ingress-logger-api<br/>host: foo.bar.com"]
    Service["Service<br/>api-server-svc<br/>NodePort 30007 -> 8000"]
    subgraph Deployment["Deployment: async-logger-api-server"]
        P1[Pod]
        P2[Pod]
        P3[Pod]
    end
    CM[ConfigMap<br/>api-service-configmap]

    Ingress --> Service
    Service --> P1 & P2 & P3
    CM -. envFrom .-> Deployment
```

### Build and publish the image

```bash
docker build -t <registry>/async-logger-api-server:latest api/
docker push <registry>/async-logger-api-server:latest
```

### Apply the manifests

```bash
kubectl apply -f api/k8s/configmap.yml
kubectl apply -f api/k8s/deployment.yml
kubectl apply -f api/k8s/service.yml
kubectl apply -f api/k8s/ingress.yml
```

The log consumer and scheduler do not currently have container images or Kubernetes manifests and must be run separately.

## API Reference

### API Server (port 8000)

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| `GET` | `/ping` | Health check. | `"pong"` |
| `GET` | `/action/{action_code}/` | Publishes an event for the given action code to Kafka. | `{"data": {"action", "created_at", "event_id"}}` |
| `GET` | `/get-logs` | Returns all persisted logs from MongoDB. | Array of log documents |

### Scheduler

| Method | Path | Description | Response |
|--------|------|-------------|----------|
| `GET` | `/` | Liveness check. | `{"message": "Scheduler running..."}` |

## Known Limitations

- **Secrets in version control.** `api/k8s/configmap.yml` stores Kafka credentials in plain text. These should be moved to a Kubernetes `Secret` and the committed credentials rotated.
- **Buffer race condition.** The consumer performs a non-atomic read-modify-write on the Redis `logs` key, and the scheduler reads and deletes it in separate calls. Events written between these operations may be lost. A Redis list (`RPUSH` / `LRANGE` + `LTRIM`) or a transaction would address this.
- **Buffer expiry.** The `logs` key carries a 300-second TTL. If the scheduler is unavailable for longer than this period, buffered events are discarded.
- **At-most-once delivery.** The consumer commits the Kafka offset before writing to Redis, so a failure between the two steps drops the event.
- **Ingress backend mismatch.** `ingress.yml` routes to a service named `logger-api-server`, whereas the service is defined as `api-server-svc`.
- **Incomplete dependency manifests.** `api/requirements.txt` omits `pymongo`, `log_consumer/requirements.txt` omits `redis`, and `scheduler/` has no `requirements.txt`.
- **No Redis service** is defined in `redis/docker-compose.yml`, despite the directory name.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
