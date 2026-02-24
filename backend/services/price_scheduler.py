"""
Price Update Scheduler
Automatically updates material prices daily using APScheduler
"""

from apscheduler.schedulers.background import BackgroundScheduler
from services.material_price_scraper import MaterialPriceScraper
from models.material_price import MaterialPrice
from utils.db import get_db
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PriceScheduler:
    """Manages automated price updates"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scraper = MaterialPriceScraper()
    
    def start(self):
        """Start the scheduler"""
        # Schedule daily update at 6 AM
        self.scheduler.add_job(
            func=self.update_prices,
            trigger='cron',
            hour=6,
            minute=0,
            id='daily_price_update',
            name='Update material prices daily',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("Price scheduler started - Daily updates at 6:00 AM")
    
    def update_prices(self):
        """Update all material prices"""
        try:
            logger.info("Starting daily price update...")
            
            db = get_db()
            
            # Fetch new prices
            new_prices = self.scraper.fetch_all_prices()
            
            # Calculate trends by comparing with yesterday's prices
            yesterday = datetime.utcnow() - timedelta(days=1)
            
            inserted_count = 0
            
            for price_data in new_prices:
                # Find yesterday's price for comparison
                previous = db.material_prices.find_one({
                    'material': price_data['material'],
                    'type': price_data['type'],
                    'location': price_data['location'],
                    'scraped_at': {'$gte': yesterday}
                }, sort=[('scraped_at', -1)])
                
                # Calculate trend
                if previous:
                    trend = MaterialPrice.calculate_trend(
                        price_data['price'],
                        previous['price']
                    )
                    price_data['trend'] = trend
                    
                    # Check for significant price increase (>5%)
                    change_percent = MaterialPrice.calculate_change_percent(
                        price_data['price'],
                        previous['price']
                    )
                    
                    if change_percent > 5:
                        logger.warning(
                            f"ALERT: {price_data['material']} {price_data['type']} "
                            f"in {price_data['location']} increased by {change_percent}%"
                        )
                else:
                    price_data['trend'] = 'same'
                
                # Insert new price record
                db.material_prices.insert_one(price_data)
                inserted_count += 1
            
            logger.info(f"Price update completed - {inserted_count} records inserted")
            
            # Clean up old data (keep only last 90 days)
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            deleted = db.material_prices.delete_many({
                'scraped_at': {'$lt': cutoff_date}
            })
            
            logger.info(f"Cleaned up {deleted.deleted_count} old records")
            
        except Exception as e:
            logger.error(f"Error updating prices: {str(e)}")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Price scheduler stopped")
