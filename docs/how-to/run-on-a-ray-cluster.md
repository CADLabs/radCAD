# Run on a Ray cluster

!!! note "Work in progress"
    Remote cluster execution via [Ray](https://ray.io/) is functional but evolving. For the latest cluster configuration options, consult the [Ray documentation](https://docs.ray.io/).

For workloads too large for a single machine, radCAD can distribute runs across a Ray cluster (AWS, GCP, Kubernetes, …) using the `RAY_REMOTE` backend.

## Install the Ray extension

=== "pip"
    ```bash
    pip install -e ".[extension-backend-ray]"
    ```
=== "Poetry"
    ```bash
    poetry install -E extension-backend-ray
    ```
=== "uv"
    ```bash
    uv sync --extra extension-backend-ray
    ```

## Provision a cluster

Export your cloud credentials (AWS shown; see Ray docs for other providers):

```bash
export BACKEND=AWS
export AWS_ACCESS_KEY_ID=***
export AWS_SECRET_ACCESS_KEY=***
```

Start a cluster (or connect to an existing one) using one of the configs in [`cluster/aws/`](https://github.com/CADLabs/radCAD/tree/master/cluster/aws):

```bash
# Single m5.large EC2 instance in us-west-2
ray up cluster/aws/minimal.yaml

# Verify the connection
ray exec cluster/aws/minimal.yaml 'echo "hello world"'
```

## Run the experiment remotely

Connect to the cluster head, then select the `RAY_REMOTE` backend:

```python
import ray
from radcad import Engine, Backend

# Connect to the cluster head node
ray.init(address="***:6379", _redis_password="***")

experiment.engine = Engine(backend=Backend.RAY_REMOTE)
result = experiment.run()
```

!!! warning
    With `RAY_REMOTE`, you are responsible for calling `ray.init(address=..., ...)` to connect to the cluster *before* running. The local `RAY` backend, by contrast, initialises a local Ray instance for you.

## Tear down the cluster

```bash
ray down cluster/aws/minimal.yaml
```

## See also

- [Choose a processing backend](choose-a-backend.md): the `RAY` (local) backend and the others.
- [`ExecutorRayRemote`](../reference/api.md#radcad.backends.Backend) in the API reference.
