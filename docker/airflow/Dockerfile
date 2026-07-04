FROM apache/airflow:2.9.0
USER root
RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-17-jdk-headless wget && \
    wget -q https://repo1.maven.org/maven2/com/google/cloud/bigdataoss/gcs-connector/hadoop3-2.2.22/gcs-connector-hadoop3-2.2.22-shaded.jar \
         -O /opt/airflow/gcs-connector.jar && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin
USER airflow
RUN pip install pyspark==3.5.0 psycopg2-binary pandas pyarrow google-cloud-storage google-cloud-bigquery db-dtypes