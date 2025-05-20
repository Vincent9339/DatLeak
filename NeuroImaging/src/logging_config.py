# logging_config.py
import os, sys, logging
from datetime import datetime

def setup_logging() -> logging.Logger:
    """Configure logging system and return logger instance."""
    try:
        log_dir = os.path.dirname(os.path.abspath(__file__))
        log_dir = os.path.join(log_dir, '.logs')
    except NameError:
        log_dir = os.path.join(os.getcwd(), '.logs')  

    os.makedirs(log_dir, exist_ok=True)
    log_filename = os.path.join(log_dir, f".leakage_detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    logging.root.handlers = []

    if os.name == 'nt':
        try:
            if sys.getwindowsversion().major < 6:  
                os.system(f'attrib +h "{log_filename}"')
            else:
                import ctypes
                ctypes.windll.kernel32.SetFileAttributesW(log_filename, 2)
        except Exception as e:
            hidden_log = os.path.join(os.path.dirname(log_filename), f".{os.path.basename(log_filename)}")
            os.rename(log_filename, hidden_log)
            log_filename = hidden_log  
            logging.warning(f"Used dot-prefix fallback: {hidden_log}")
            
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, mode='w'),
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("Logging setup complete")
    logger.info(f"Log file location: {log_filename}")
    
    return logger
