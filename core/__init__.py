import logging
import os

# Set up global logger
log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../logs/debug.log")
os.makedirs(os.path.dirname(log_path), exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_path, mode="a"),
        logging.StreamHandler()
    ]
)
