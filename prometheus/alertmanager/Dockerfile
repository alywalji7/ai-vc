FROM prom/alertmanager:latest

# Copy configuration file
COPY alertmanager.yml /etc/alertmanager/

# Set ownership and permissions
USER root
RUN chown -R nobody:nobody /etc/alertmanager

# Switch back to the non-root user
USER nobody

# Expose the default AlertManager port
EXPOSE 9093

# Command to run AlertManager
ENTRYPOINT [ "/bin/alertmanager" ]
CMD [ "--config.file=/etc/alertmanager/alertmanager.yml", \
      "--storage.path=/alertmanager", \
      "--web.external-url=http://alertmanager:9093" ]