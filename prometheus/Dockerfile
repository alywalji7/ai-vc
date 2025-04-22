FROM prom/prometheus:latest

# Copy our custom configuration
COPY prometheus.yml /etc/prometheus/prometheus.yml
COPY rules/ /etc/prometheus/rules/

# Set user to run prometheus
USER 65534