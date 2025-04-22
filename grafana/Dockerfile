FROM grafana/grafana:latest

# Set the environment variable for the default data source
ENV GF_PATHS_PROVISIONING="/etc/grafana/provisioning"

# Set up user
USER root

# Copy provisioning configurations
COPY provisioning/datasources /etc/grafana/provisioning/datasources
COPY provisioning/dashboards /etc/grafana/provisioning/dashboards
COPY dashboards /var/lib/grafana/dashboards

# Set permissions
RUN chmod -R 777 /etc/grafana /var/lib/grafana/dashboards

# Switch back to grafana user
USER grafana

# Expose the port
EXPOSE 3000

# Command to run Grafana
ENTRYPOINT ["/run.sh"]