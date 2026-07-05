# DevopsMlopsFinal

By Noah Hemon, Antoine Iglesias-Tallon and Nassim Ainine.

## Monitoring

- Prometheus UI: http://localhost:9090
- Grafana dashboard: http://localhost:3000 (login: admin / admin)
- The backend exposes metrics at /metrics, scraped by Prometheus every 5 seconds.
- The Grafana dashboard "Backend Monitoring" shows request volume, prediction latency (p95), error rate, and backend uptime.