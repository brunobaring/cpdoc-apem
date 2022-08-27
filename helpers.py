import requests, time, random



def sleep():
    time_to_sleep = random.randint(2, 4)
    print(f'Sleeping {time_to_sleep} seconds...\n', flush=True)
    time.sleep(time_to_sleep)



def make_request(url):
    print(f'Requesting... {url}')
    response = requests.get(url=url)
    if response.status_code != 200:
        print(response.status_code, flush=True)
    return response