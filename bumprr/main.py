import time

# Local imports
from config import get_config
from arrs import test_and_set_api_version, fetch_queue, process_queue_item

print("Starting Bumprr...")

print("Checking config file...")

config = get_config()

print("Config file loaded successfully.\n")

poll_interval = config.get("poll_interval", 60)
sonarr_enabled = config.get("sonarr", {}).get("enabled", False)
radarr_enabled = config.get("radarr", {}).get("enabled", False)

if sonarr_enabled:
    print("Sonarr enabled in config file, testing connection...")
    try: 
        test_and_set_api_version("sonarr")
    except Exception as e:
        print(f"Failed to connect to Sonarr: {e}. Disabling Sonarr integration.")
        sonarr_enabled = False
if radarr_enabled:
    print("Radarr enabled in config file, testing connection...")
    try:
        test_and_set_api_version("radarr")
    except Exception as e:
        print(f"Failed to connect to Radarr: {e}. Disabling Radarr integration.")
        radarr_enabled = False



while True:
    try:

        # Main logic would go here
        if sonarr_enabled:
            sonarr_queue = fetch_queue("sonarr")
            sonarr_queue_warnings = [item for item in sonarr_queue if item.get('trackedDownloadStatus') == 'warning']
            print(f"Found {len(sonarr_queue_warnings)} warning items in Sonarr queue to process.")
            for item in sonarr_queue_warnings:
                process_queue_item(item, "sonarr")


        print(f"\n Queue processing complete. Waiting for {poll_interval} seconds before next processing...\n")
        time.sleep(poll_interval)

    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        break
    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(poll_interval)