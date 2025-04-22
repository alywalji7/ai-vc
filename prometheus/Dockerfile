FROM prom/prometheus:latest

# Copy the Prometheus configuration file
COPY prometheus.yml /etc/prometheus/
COPY rules/ /etc/prometheus/rules/

# Set ownership and permissions
USER root
RUN mkdir -p /etc/prometheus/rules && \
    chown -R nobody:nobody /etc/prometheus

# Switch back to the non-root user
USER nobody

# Expose the default Prometheus port
EXPOSE 9090

# Command to run Prometheus
ENTRYPOINT [ "/bin/prometheus" ]
CMD [ "--config.file=/etc/prometheus/prometheus.yml", \
      "--storage.tsdb.path=/prometheus", \
      "--web.console.libraries=/usr/share/prometheus/console_libraries", \
      "--web.console.templates=/usr/share/prometheus/consoles", \
      "--web.enable-lifecycle" ]