import time
import logging
from typing import Callable, Optional

logger = logging.getLogger("server-monitor.agent.scheduler")

class MetricCollectionScheduler:
    """
    Schedules metric collection loop every interval_seconds (default 10 seconds).
    """
    def __init__(self, callback: Callable, interval_seconds: float = 10.0):
        self.callback = callback
        self.interval = interval_seconds
        self.running = False

    def start(self, max_runs: Optional[int] = None):
        self.running = True
        logger.info(f"Starting MetricCollectionScheduler every {self.interval}s...")
        runs = 0
        while self.running:
            try:
                self.callback()
            except Exception as e:
                logger.error(f"Error in metric collection iteration: {e}", exc_info=True)

            runs += 1
            if max_runs and runs >= max_runs:
                break
            time.sleep(self.interval)

    def stop(self):
        self.running = False
        logger.info("MetricCollectionScheduler stopped.")
