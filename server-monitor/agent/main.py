import sys
import os
import json
import logging
import argparse

# Add parent directory to sys.path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.collector import MetricsCollector
from agent.scheduler import MetricCollectionScheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("server-monitor.agent")

def main():
    parser = argparse.ArgumentParser(description="Linux Host Monitoring Agent")
    parser.add_argument("--once", action="store_true", help="Run a single metric collection pass and output JSON")
    parser.add_argument("--interval", type=float, default=10.0, help="Metric collection interval in seconds")
    args = parser.parse_args()

    collector = MetricsCollector()

    if args.once:
        data = collector.collect_all(use_cache=False)
        print(json.dumps(data, indent=2))
        sys.exit(0)

    logger.info("Linux Host Monitoring Agent starting in daemon mode...")
    
    def on_collect():
        snapshot = collector.collect_all(use_cache=False)
        logger.info(f"Collected snapshot at {snapshot['timestamp']}: CPU {snapshot['cpu']['usage_percent']}%, RAM {snapshot['memory']['usage_percent']}%")

    scheduler = MetricCollectionScheduler(callback=on_collect, interval_seconds=args.interval)
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Agent daemon interrupted by user. Exiting.")
        scheduler.stop()

if __name__ == "__main__":
    main()
