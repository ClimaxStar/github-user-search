import pandas as pd
import requests
from datetime import datetime
import time
import os
import logging
import json
import re

states = [
    'Alabama',
    'Alaska', 
    'Arizona', 
    'Arkansas', 
    'California',
    'Colorado', 
    'Connecticut', 
    'Delaware', 
    'Florida', 
    'Georgia',
    'Hawaii', 
    'Idaho', 
    'Illinois', 
    'Indiana', 
    'Iowa',
    'Kansas', 
    'Kentucky', 
    'Louisiana', 
    'Maine', 
    'Maryland',
    'Massachusetts', 
    'Michigan', 
    'Minnesota', 
    'Mississippi', 
    'Missouri',
    'Montana', 
    'Nebraska', 
    'Nevada', 
    'New Hampshire', 
    'New Jersey',
    'New Mexico', 
    'New York', 
    'North Carolina', 
    'North Dakota', 
    'Ohio',
    'Oklahoma', 
    'Oregon', 
    'Pennsylvania', 
    'Rhode Island', 
    'South Carolina',
    'South Dakota', 
    'Tennessee', 
    'Texas', 
    'Utah', 
    'Vermont',
    'Virginia', 
    'Washington', 
    'West Virginia', 
    'Wisconsin', 
    'Wyoming'
]

config_path = 'config.json'
proxies = {}


def validate_city(state, city):
    try:
        df = pd.read_csv(f"states/{state}.csv")
        if city in df['city_state_short'].values:
            return True
    except FileNotFoundError:
        print(f"CSV file for {state} not found.")
    return False


def is_leap_year(year):
    if year % 400 == 0:
        return 1
    elif year % 100 == 0:
        return 0
    elif year % 4 == 0:
        return 1
    return 0


def analyze_log_file(log_file_path):
    success_count = 0
    error_count = 0
    
    with open(log_file_path, 'r') as file:
        for line in file:
            if re.search(r'INFO - ', line):
                success_count += 1
            elif re.search(r'ERROR - ', line):
                error_count += 1
    
    return success_count, error_count


def setup_logger(state, city):
    dir_path = os.path.join('users', state, city)
    os.makedirs(dir_path, exist_ok=True)
    logger = logging.getLogger(f'{state}-{city}_logger')
    logger.setLevel(logging.DEBUG)
    log_file_path = os.path.join(dir_path, f"{state}-{city}.log")
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def fetch_github_data_from_state(state):
    file_path = 'states/' + state + '.csv'
    try:
        df = pd.read_csv(file_path)
        cities = df['city_state_short'].dropna().str.strip().tolist()
        for city in cities:
            fetch_github_data_from_city(state, city)
    except Exception as e:
        print(f"Error reading CSV file: {e}")


def fetch_github_data_from_city(state, city):
    days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    current_year = 2020
    current_month = 1
    logger = setup_logger(state, city)

    while current_year > 2017:
        last_day = days[current_month-1]
        if current_month == 2: last_day += is_leap_year(current_year)
        start_date = datetime(current_year, current_month, 1)
        end_date = datetime(current_year, current_month, last_day)
        
        fetch_github_accounts(state, city, start_date, end_date, logger)
        fetch_github_users(state, city, current_year, current_month, logger)

        if current_month == 12: 
            current_month = 1
            current_year -= 1
        else:
            current_month += 1
    log_path = os.path.join('users', state, city, f"{state}-{city}.log")
    success_count, error_count = analyze_log_file(log_path)
    logger.debug(f"Number of Success: {success_count}")
    logger.debug(f"Number of Error: {error_count}")
    print(f"Number of Success: {success_count}")
    print(f"Number of Error: {error_count}")
    logger.handlers.clear()


def fetch_github_accounts(state, city, start_date, end_date, logger, page=1):
    try:
        per_page = 100
        url = f"https://api.github.com/search/users?q=created:{start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')} location:\"{city}\" type:user&per_page={per_page}&page={page}"

        time.sleep(1)
        response = requests.get(url, proxies=proxies)
        data = response.json()

        while 'items' not in data:
            logger.error(f"[ACCOUNT] Exceed the github api limitiation for [{state} - {city}]")
            time.sleep(1)
            response = requests.get(url, proxies=proxies)
            data = response.json()

        records = [{
            'username': item['login'],
            'User ID': item['id'],
            'Profile URL': item['html_url'],
        } for item in data.get('items', [])]

        save_accounts(state, city, start_date, end_date, records)

        total_count = data.get('total_count', 0)
        if page * per_page < total_count:
            fetch_github_accounts(state, city, start_date, end_date, logger, page + 1)
        else:
            data = {
                "state": state,
                "city": city,
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d'),
                "count": total_count
            }
            st = pd.DataFrame([data])
            count_csv_path = os.path.join('users', state, city, f"{state}-{city}.csv")
            if os.path.isfile(count_csv_path):
                st.to_csv(count_csv_path, index=False, mode='a', header=False, encoding='utf-8')
            else:
                st.to_csv(count_csv_path, index=False, mode='w', header=True, encoding='utf-8')
    except Exception as e:
        logger.error(f"Error fetching GitHub data for [{state} - {city}]: {e}")
        print(f"Error fetching GitHub data for [{state} - {city}]: {e}")


def save_accounts(state, city, start_date, end_date, records):
    filename = f"{start_date.year}-{start_date.month}.csv"
    dir_path = os.path.join('accounts', state, city)
    file_path = os.path.join(dir_path, filename)

    os.makedirs(dir_path, exist_ok=True)
    print(state, city, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), len(records))

    columns = ['username', 'User ID', 'Profile URL']

    if not records:
        df = pd.DataFrame(columns=columns)
        df.to_csv(file_path, index=False, mode='w', header=True, encoding='utf-8')
    else:
        df = pd.DataFrame(records)
        if os.path.isfile(file_path):
            df.to_csv(file_path, index=False, mode='a', header=False, encoding='utf-8')
        else:
            df.to_csv(file_path, index=False, mode='w', header=True, encoding='utf-8')


def fetch_github_users(state, city, year, month, logger):
    filename = f"{year}-{month}.csv"
    state_path = os.path.join('accounts', state)
    city_path = os.path.join(state_path, city)
    file_path = os.path.join(city_path, filename)
    try:
        df = pd.read_csv(file_path)
        accounts = df['username'].dropna().str.strip().tolist()
        for username in accounts:
            fetch_github_user(state, city, filename, username, logger)
    except Exception as e:
        logger.error(f"Error reading CSV file: states/{state}.csv")
        print(f"Error reading CSV file: {e}")


def fetch_github_user(state, city, filename, username, logger):
    try:
        url = f"https://api.github.com/users/{username}"
        time.sleep(1)
        initialResponse = requests.get(url, proxies=proxies)
        initialData = initialResponse.json()
        
        while 'login' not in initialData:
            print(f"[USER-Initial] Exceed the github api limitiation while fetching data for [{username}]")
            logger.error(f"[USER-Initial] Exceed the github api limitiation while fetching data for [{username}]")
            logger.error(json.dumps(initialData))
            time.sleep(1)
            initialResponse = requests.get(url, proxies=proxies)
            initialData = initialResponse.json()

        record = {
            'username': initialData['login'],
            'id': initialData['id'],
            'node_id': initialData['node_id'],
            'avatar_url': initialData['avatar_url'],
            'name': initialData['name'],
            'company': initialData['company'],
            'blog': initialData['blog'],
            'location': initialData['location'],
            'email': initialData['email'],
            'hireable': initialData['hireable'],
            'bio': initialData['bio'],
            'twitter_username': initialData['twitter_username'],
            'public_repos': initialData['public_repos'],
            'public_gists': initialData['public_gists'],
            'followers': initialData['followers'],
            'following': initialData['following'],
            'facebook': '',
            'instagram': '',
            'linkedin': '',
            'npm': '',
            'reddit': '',
            'twitch': '',
            'youtube': '',
            'mastodon': '',
            'hometown': '',
            'twitter': '',
            'generic': '',
            'created_at': initialData['created_at'],
            'updated_at': initialData['updated_at']
        }

        url = f"https://api.github.com/users/{username}/social_accounts"

        time.sleep(1)
        socialResponse = requests.get(url, proxies=proxies)
        socialData = socialResponse.json()

        while not isinstance(socialData, list):
            print(f"[USER-Social] Exceed the github api limitiation while fetching data for [{username}]")
            logger.error(f"[USER-Social] Exceed the github api limitiation while fetching data for [{username}]")
            logger.error(json.dumps(socialData))
            time.sleep(1)
            socialResponse = requests.get(url, proxies=proxies)
            socialData = socialResponse.json()

        for social in socialData:
            if(social['provider'] == 'generic'):
                record[social['provider']] += social['url'] + ', '
            else:
                 record[social['provider']] = social['url']

        record['generic'] = record['generic'][:-2]

        url = f"https://api.github.com/users/{username}/events/public"

        time.sleep(1)
        emailResponse = requests.get(url, proxies=proxies)
        emailData = emailResponse.json()

        while not isinstance(emailData, list):
            print(f"[USER-Email] Exceed the github api limitiation while fetching data for [{username}]")
            logger.error(f"[USER-Email] Exceed the github api limitiation while fetching data for [{username}]")
            logger.error(json.dumps(emailData))
            time.sleep(1)
            emailResponse = requests.get(url, proxies=proxies)
            emailData = emailResponse.json()

        emailString = ""

        final=set()
        for x in emailData:
            if x['payload'].get('commits'):
                final.add(x['payload']['commits'][0]['author']['email'])
        for mail in final:
            emailString += mail + ', '

        record['email'] = emailString[:-2]

        logger.info(f"User data collected successfully for [{username}]")
        save_user(state, city, filename, record)

    except Exception as e:
        logger.error(f"Error fetching GitHub data for [{username}]: {e}")
        print(f"Error fetching GitHub data for [{username}]: {e}")


def save_user(state, city, filename, record):
    file_path = os.path.join('users', state, city, filename)
    df = pd.DataFrame([record])

    print(record)

    columns = [
        'username', 'id', 'node_id', 'avatar_url', 'name', 'company', 'blog', 'location', 'email', 'hireable', 'bio',
        'twitter_username', 'public_repos', 'public_gists', 'followers', 'following', 'facebook', 'instagram', 'linkedin',
        'npm', 'reddit', 'twitch', 'youtube', 'mastodon', 'hometown', 'twitter', 'generic', 'created_at', 'updated_at'
    ]

    if os.path.isfile(file_path):
        df.to_csv(file_path, mode='a', header=False, index=False, columns=columns, encoding='utf-8')
    else:
        df.to_csv(file_path, mode='w', header=True, index=False, columns=columns, encoding='utf-8')


def main():
    global proxies
    # State input with validation
    while True:
        stateInput = input(f"Enter State Name or press Enter for 'all': ")
        if stateInput == "":
            state = "all"
            break
        elif stateInput in states:
            state = stateInput
            break
        else:
            print(f"Invalid input. Please enter correct state name.")

    print("State: ", state)

    # City input with validation
    if state != "all":
        while True:
            cityInput = input(f"Enter City Name or press Enter for 'all': ")
            if cityInput == "":
                city = "all"
                break
            elif validate_city(state, cityInput):
                city = cityInput
                break
            else:
                print(f"Invalid input. Please enter correct city name")
    else:
        city = "all"
    print("City Name: ", city)

    # Set Proxy Information
    if not os.path.exists(config_path):
        print(f"The configuration file {config_path} does not exist.")
        return
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
            proxies = {
                'http': f"http://{config['username']}:{config['password']}@{config['domain']}:{config['port']}",
                'https': f"http://{config['username']}:{config['password']}@{config['domain']}:{config['port']}"
            }
            print(proxies)
    except Exception as e:
        print(f"Error decoding JSON: {e}")
        return


    if state == "all":
        for state_name in states:
            fetch_github_data_from_state(state_name)
    else:
        if city == "all":
            fetch_github_data_from_state(state)
        else:
            fetch_github_data_from_city(state, city)


if __name__ == "__main__":
    main()