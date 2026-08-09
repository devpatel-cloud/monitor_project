# DuckDNS & IPv6 Synchronization Guide

The monitoring platform integrates directly with the host's existing `duckdns-ipv6.service` and `/usr/local/bin/duckdns-ipv6.sh`.

## Security Rules
- The DuckDNS token is loaded from `/etc/server-monitor/config.yaml` or environment.
- The token is NEVER exposed via REST API responses or embedded in frontend JS bundles.
- Mismatches between local host IPv6 and DuckDNS AAAA records automatically trigger an alert.
