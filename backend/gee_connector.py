import ee
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class GEEConnector:
    def __init__(self, project_id='gaias-ark'):
        self.project_id = project_id
        self.initialized = False
        
    def initialize(self):
        """Initialize Google Earth Engine"""
        try:
            ee.Initialize(project=self.project_id)
            self.initialized = True
            logger.info(f"GEE initialized with project: {self.project_id}")
            return True
        except Exception as e:
            logger.error(f"GEE initialization failed: {e}")
            return False
    
    def get_kenyan_coast_roi(self):
        """Get Kenya coastal region of interest"""
        if not self.initialized:
            self.initialize()
            
        return ee.Geometry.Polygon([
            [[41.5717961934335, -1.6660673751001729],
             [40.797260060621, -1.9405892862517224],
             [40.1545598653085, -2.7693492692094908],
             [39.533832326246, -3.9866897907459995],
             [39.1987493184335, -4.671372188469907],
             [39.4734075215585, -4.720644703111153],
             [40.291888966871, -3.005255303437709],
             [40.2424504903085, -2.7748360052373107],
             [40.4951360371835, -2.55534723599033],
             [40.665424123121, -2.5663225925438042],
             [41.4509465840585, -1.874707854125858]]
        ])
    
    def get_mangrove_data(self, roi=None):
        """Fetch mangrove data from GEE"""
        if not self.initialized:
            if not self.initialize():
                return None
                
        if roi is None:
            roi = self.get_kenyan_coast_roi()
            
        try:
            # Use Global Mangrove Watch dataset
            mangroves = ee.ImageCollection("LANDSAT/MANGROVE_FORESTS")
            
            # Get latest mangrove extent
            latest = mangroves.sort('system:time_start', False).first()
            
            # Clip to ROI
            mangrove_roi = latest.clip(roi)
            
            return mangrove_roi
            
        except Exception as e:
            logger.error(f"Error fetching mangrove data: {e}")
            return None
    
    def export_to_drive(self, image, description, folder='gaia_ark_exports'):
        """Export image to Google Drive"""
        if not self.initialized:
            if not self.initialize():
                return None
                
        task = ee.batch.Export.image.toDrive(
            image=image,
            description=description,
            folder=folder,
            scale=30,
            maxPixels=1e9
        )
        
        task.start()
        logger.info(f"Export task started: {description}")
        return task
    
    def monitor_task(self, task):
        """Monitor GEE task status"""
        import time
        
        while task.active():
            logger.info(f"Task {task.id} status: {task.status()['state']}")
            time.sleep(30)
            
        final_status = task.status()
        if final_status['state'] == 'COMPLETED':
            logger.info(f"Task {task.id} completed successfully")
        else:
            logger.error(f"Task {task.id} failed: {final_status}")
            
        return final_status

# Global instance
gee = GEEConnector()

if __name__ == "__main__":
    # Test GEE connection
    if gee.initialize():
        roi = gee.get_kenyan_coast_roi()
        print(f"Kenya ROI bounds: {roi.bounds().getInfo()}")
        
        mangroves = gee.get_mangrove_data(roi)
        if mangroves:
            print("Mangrove data fetched successfully")
    else:
        print("GEE initialization failed")