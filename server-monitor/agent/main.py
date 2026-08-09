import sys
import os
import json
import logging
import argparse

# Add parent directory to sys.path if needed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent.collector import MetricsCollector
from agent.scheduler import MetricCollectionScheduler
from backend.app.database.database import engine, Base, SessionLocal
from backend.app.database.repository import save_snapshot_to_db
from backend.app.services.alerts import alert_engine

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

    # Guarantee SQLite database tables exist
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.warning(f"Could not create database tables on startup: {e}")

    collector = MetricsCollector()

    if args.once:
        data = collector.collect_all(use_cache=False)
        print(json.dumps(data, indent=2))
        sys.exit(0)

    logger.info("Linux Host Monitoring Agent starting in daemon mode...")

    # Immediate initial collection pass so DB has metrics right away
    try:
        init_snapshot = collector.collect_all(use_cache=False)
        db_init = SessionLocal()
        try:
            save_snapshot_to_db(db_init, init_snapshot)
            alert_engine.evaluate_snapshot(db_init, init_snapshot)
        finally:
            db_init.close()
    except Exception as e:
        logger.error(f"Initial collection pass error: {e}")
    
    def on_collect():
        snapshot = collector.collect_all(use_cache=False)
        db = SessionLocal()
        try:
            save_snapshot_to_db(db, snapshot)
            alert_engine.evaluate_snapshot(db, snapshot)
        except Exception as e:
            logger.error(f"Error persisting snapshot/alerts: {e}")
        finally:
            db.close()

        logger.info(f"Collected and persisted snapshot at {snapshot['timestamp']}: CPU {snapshot['cpu']['usage_percent']}%, RAM {snapshot['memory']['usage_percent']}%")

    scheduler = MetricCollectionScheduler(callback=on_collect, interval_seconds=args.interval)
    try:
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Agent daemon interrupted by user. Exiting.")
        scheduler.stop()

if __name__ == "__main__":
    main()
