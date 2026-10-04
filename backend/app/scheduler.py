from apscheduler.schedulers.background import BackgroundScheduler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start_scheduler():
    scheduler = BackgroundScheduler()
    
    # 1. Phase 6 PO Generator Job (Runs nightly at 2 AM)
    from scripts.po_generator import generate_pos
    def run_po_generator():
        try:
            logger.info("Starting nightly PO Generator job...")
            generate_pos(dry_run=False)
            logger.info("PO Generator job completed successfully.")
        except Exception as e:
            logger.error(f"PO Generator job failed: {e}")
            
    scheduler.add_job(run_po_generator, 'cron', hour=2, minute=0)
    
    # 2. Phase 4 Jobs (Placeholder)
    # scheduler.add_job(run_demand_forecast, 'cron', hour=1, minute=0)
    
    scheduler.start()
    logger.info("Background Scheduler started. Nightly jobs registered.")
