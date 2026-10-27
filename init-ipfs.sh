#!/bin/sh
set -eu
case "${FLOW_DOMAIN:-}" in
  ""|*[!A-Za-z0-9.-]*|.*|*.) echo "Invalid FLOW_DOMAIN" >&2; exit 1 ;;
esac
case "$FLOW_DOMAIN" in
  *.*) ;;
  *) echo "FLOW_DOMAIN must be a DNS name" >&2; exit 1 ;;
esac
# Run by the official Kubo image before its daemon, on each startup.
ipfs config --json Gateway.NoFetch true
ipfs config --json Gateway.NoDNSLink true
ipfs config --json Gateway.PublicGateways "{\"$FLOW_DOMAIN\":{\"Paths\":[],\"UseSubdomains\":false,\"NoDNSLink\":false}}"
ipfs config Datastore.StorageMax 10GB
