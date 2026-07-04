# Engineering Decisions

## 1. Why local[*] instead of a Spark cluster in Phase 1

Running PySpark in `local[*]` mode uses all available CPU cores on the host machine
without requiring a separate cluster process. For Phase 1, the dataset is small
(6 rows per daily run) and the value being demonstrated is the transform logic,
not cluster management.

The alternative — a standalone Spark master/worker setup in Docker — was attempted
and abandoned after debugging a 20-minute silent hang caused by the Spark driver
needing a bidirectional network callback to the master that Docker's internal
networking made unreliable. The engineering decision was: don't fight infrastructure
when the infrastructure adds no value at this scale.

The same transform code runs unchanged in Phase 2 — only the SparkSession
configuration differs. That's the actual portability claim worth making.

## 2. Why Cloud Composer was rejected

Cloud Composer is a managed Airflow deployment on GKE. Its minimum cost is
approximately $300-400/month even when idle, because it runs a persistent
Kubernetes cluster regardless of whether any DAGs are executing.

For a portfolio project targeting GCP Always-Free tier, this is a non-starter.
The decision was to run Airflow locally (Phase 1) and document the Composer
rejection explicitly rather than pretend the managed service was used.

This is also the correct production decision for small-to-medium pipelines where
the operational overhead of Composer is not justified by DAG complexity. A
self-managed Airflow deployment on an e2-micro Always-Free VM achieves the same
orchestration for $0/month.

## 3. Why the shaded JAR instead of spark.jars.packages

`spark.jars.packages` downloads dependencies from Maven Central at runtime using
Spark's internal resolver. This requires outbound internet access from the Spark
driver process, which was unavailable inside the Docker container due to DNS
resolution failures in the local network environment.

The shaded JAR (`gcs-connector-hadoop3-2.2.22-shaded.jar`) bundles all its
dependencies including Guava, avoiding a version conflict with Spark 3.5's bundled
Hadoop libraries that caused a `NoClassDefFoundError` on
`GoogleHadoopFileSystemConfiguration` when using the non-shaded variant.

The JAR is downloaded at Docker image build time via `wget` in the Dockerfile,
ensuring the dependency is resolved on the host machine where internet access
works, not inside the container at runtime. This makes the image self-contained
and portable.