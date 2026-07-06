#!/bin/sh
# If Render Secret File exists, use it instead of the baked-in config
if [ -f /etc/secrets/prometheus.yml ]; then
  cp /etc/secrets/prometheus.yml /etc/prometheus/prometheus.yml
  echo "Using Render Secret File config"
fi
exec /bin/prometheus "$@"
