from api import fetch_data
from config import add_to_config, get_config
from notifications import send_discord_notification

actions_sorted = [
  'blocklist_and_search',
  'blocklist',
  'refresh_and_redownload',
  'remove',
  'no_action',
]


def test_and_set_api_version(service_name):
  version_response = fetch_data(service_name, '', full_path_override='api')
  print(f"Found {service_name.capitalize()} API Version: {version_response.get('current', 'unknown')}")
  add_to_config(service_name, 'api_version', version_response.get('current', 'v3'))  
  print(f"Checking {service_name.capitalize()} system status...")
  status_response =  fetch_data(service_name, 'system/status')
  if 'appName' in status_response and status_response['appName'] == service_name.capitalize():
      print(f"Connected to {service_name.capitalize()}: {status_response['appName']} - Version: {status_response['version']}")
      print(f"{service_name.capitalize()} implementation enabled.\n")
  else:
      raise Exception(f"Unexpected response from {service_name.capitalize()} API.")
  

def fetch_queue(service_name):
  print(f"Fetching {service_name.capitalize()} queue...")
  queue = fetch_data(service_name, 'queue', params={'pageSize': 100000000})
  print(f"Fetched {len(queue.get('records', []))} items from {service_name.capitalize()} queue.")
  return queue.get('records', [])

def process_queue_item(item, service_name):
  
  # Extract needed info from item
  title = item.get('title', 'Unknown Title')
  tracked_download_status = item.get('trackedDownloadStatus', 'Unknown Status')
  tracked_download_state = item.get('trackedDownloadState', 'Unknown State')
  status_messages = item.get('statusMessages', [])

  # Logging
  print(f"\nProcessing item: {title} from {service_name.capitalize()} queue.")
  print(f"    Tracked Download Status: {tracked_download_status}")
  print(f"    Tracked Download State: {tracked_download_state}\n")

  # Get Config Settings

  config = get_config()
  config_for_service = config.get(service_name, {})

  default_actions = config_for_service.get('action_default', {})
  specific_messages = config_for_service.get(f'{tracked_download_state}_messages', {})

  actions = []
  messages_logged = []
  # Proccess
  for message_title in status_messages: # Outer messages array

    for message in message_title.get('messages', []): # Inner messages array
        print('        Status Message: ', message)
        found_action = next((specific_messages[specific_message_test] for specific_message_test in specific_messages if specific_message_test in message), None)
        if (found_action is None):
            found_action = default_actions.get(tracked_download_state, "no_action")
        actions.append(found_action)
        messages_logged.append(message)
    

  return action_processor(item, actions, service_name, messages_logged)

# Item Action Processor
def action_processor(item, actions, service_name, messages_logged):
  final_action = next((action for action in actions_sorted if action in actions), "no_action")

  send_discord_notification(
     f"{service_name.capitalize()} Queue Item Processed",
     f"Item: `{item.get('title', 'Unknown Title')}`\n Messages:\n```- {'\n- '.join(messages_logged)}```\nAction Taken: `{final_action.replace('_', ' ').capitalize()}`"
  )

  if final_action == 'blocklist_and_search':
      return process_blocklist_and_search(item, service_name)
  elif final_action == 'blocklist':
      return process_blocklist(item, service_name)
  elif final_action == 'refresh_and_redownload':
      return process_refresh_and_redownload(item, service_name)
  elif final_action == 'remove':
      return process_remove(item, service_name)
  else:
      print("    No action taken for this item.")
      return None

# Individual Action Handlers

def process_blocklist_and_search(item, service_name):
  item_id = item.get('id')
  if (item_id is None):
      print("    Error: Item ID not found, cannot blocklist.")
      return None
  print(f"    Blocklisting and searching item ID {item_id} in {service_name.capitalize()}...")
  response = fetch_data(
     service_name, 
     f'queue/{item_id}', 
     method='DELETE', 
     params={
        'blocklist': 'true',
        'removeFromClient': 'true',
        'skipRedownload': 'false'
     })
  
  if response is not None:
      print(f"    Blocklisted and searched item ID {item_id} in {service_name.capitalize()}.")
  return response


def process_blocklist(item, service_name):
  item_id = item.get('id')
  if (item_id is None):
      print("    Error: Item ID not found, cannot blocklist.")
      return None
  print(f"    Blocklisting item ID {item_id} in {service_name.capitalize()}...")
  response = fetch_data(
     service_name, 
     f'queue/{item_id}', 
     method='DELETE', 
     params={
        'blocklist': 'true',
        'removeFromClient': 'true',
        'skipRedownload': 'true'
     })
  
  if response is not None:
      print(f"    Blocklisted item ID {item_id} in {service_name.capitalize()}.")
  return response


def process_refresh_and_redownload(item, service_name):
  item_id = item.get('id')
  if (item_id is None):
      print("    Error: Item ID not found, cannot refresh and redownload.")
      return None
  print(f"    Refreshing Series Id {item.get('seriesId')} for item ID {item_id} in {service_name.capitalize()}...")
  response1 = fetch_data(
     service_name,
     'command',
     method='POST',
        body={
          'seriesId': item.get('seriesId'),
          'name': 'RefreshSeries'
        })
  
  if response1 is not None:
      print(f"    Refreshed Series Id {item.get('seriesId')} for item ID {item_id} in {service_name.capitalize()}.")

  print(f'    Redownling item Id {item_id}...')
  response2 = fetch_data(
     service_name,
     f'queue/{item_id}',
     method='DELETE',
     params={
        'blocklist': 'false',
        'removeFromClient': 'true',
        'skipRedownload': 'false'
     })
  if response2 is not None:
      print(f"    Redownloaded item ID {item_id} in {service_name.capitalize()}.")
  return response1


def process_remove(item, service_name):
  item_id = item.get('id')
  if (item_id is None):
      print("    Error: Item ID not found, cannot remove from queue.")
      return None
  print(f"    Removing item ID {item_id} from {service_name.capitalize()} queue...")
  response = fetch_data(
     service_name, 
     f'queue/{item_id}', 
     method='DELETE', 
     params={
        'blocklist': 'false',
        'removeFromClient': 'true',
        'skipRedownload': 'true'
     })
  
  if response is not None:
      print(f"    Removed item ID {item_id} from {service_name.capitalize()} queue.")
  return response