import pandas as pd
import requests
from datetime import datetime
import time
import os
import logging
import json

logging.basicConfig(filename='error.log', level=logging.ERROR,
                    format='%(asctime)s %(levelname)s:%(message)s')

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


def fetch_github_accounts_from_state(state_name, start_date, end_date):
    file_path = 'states/' + state_name + '.csv'
    try:
        df = pd.read_csv(file_path)
        cities = df['city_state_short'].dropna().str.strip().tolist()
        for city in cities:
            fetch_github_accounts_from_city(state_name, city, start_date, end_date)
    except Exception as e:
        logging.error(f"Error reading CSV file: states/{state_name}.csv")
        print(f"Error reading CSV file: {e}")


def fetch_github_accounts_from_city(state, city, start_date, end_date, page=1):
    try:
        per_page = 100
        url = f"https://api.github.com/search/users?q=created:{start_date.strftime('%Y-%m-%d')}..{end_date.strftime('%Y-%m-%d')} location:\"{city}\" type:user&per_page={per_page}&page={page}"
        
        time.sleep(3)
        response = requests.get(url)
        data = response.json()

        while 'items' not in data:
            logging.error("[ACCOUNT] Exceed the github api limitiation")
            time.sleep(600)
            response = requests.get(url)
            data = response.json()

        records = [{
            'username': item['login'],
            'User ID': item['id'],
            'Profile URL': item['html_url'],
        } for item in data.get('items', [])]

        write_accounts_data(state, city, start_date, end_date, records)

        total_count = data.get('total_count', 0)
        if page * per_page < total_count:
            fetch_github_accounts_from_city(state, city, start_date, end_date, page + 1)
    except Exception as e:
        logging.error(f"Error fetching GitHub data for {city}: {e}")
        print(f"Error fetching GitHub data for {city}: {e}")


def write_accounts_data(state, city, start_date, end_date, records):
    filename = f"{start_date.strftime('%Y-%m-%d')}-{end_date.strftime('%Y-%m-%d')}.csv"
    dir_path = os.path.join('accounts', state, city)
    file_path = os.path.join(dir_path, filename)

    os.makedirs(dir_path, exist_ok=True)
    print(state, city, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), len(records))

    data = {
        "state": state,
        "city": city,
        "start_date": start_date.strftime('%Y-%m-%d'),
        "end_date": end_date.strftime('%Y-%m-%d'),
        "count": len(records)
    }
    st = pd.DataFrame([data])
    if os.path.isfile('account_count.csv'):
        st.to_csv('account_count.csv', index=False, mode='a', header=False, encoding='utf-8')
    else:
        st.to_csv('account_count.csv', index=False, mode='w', header=True, encoding='utf-8')

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


def fetch_github_users_from_state(state_name, start_date, end_date):
    file_path = 'states/' + state_name + '.csv'
    try:
        df = pd.read_csv(file_path)
        cities = df['city_state_short'].dropna().str.strip().tolist()
        for city in cities:
            fetch_github_users_from_city(state_name, city, start_date, end_date)
    except Exception as e:
        logging.error(f"Error reading CSV file: states/{state_name}.csv")
        print(f"Error reading CSV file: {e}")


def fetch_github_users_from_city(state_name, city, start_date, end_date):
    filename = f"{start_date.strftime('%Y-%m-%d')}-{end_date.strftime('%Y-%m-%d')}.csv"
    state_path = os.path.join('accounts', state_name)
    city_path = os.path.join(state_path, city)
    file_path = os.path.join(city_path, filename)
    try:
        df = pd.read_csv(file_path)
        accounts = df['username'].dropna().str.strip().tolist()
        for account in accounts:
            fetch_github_data_for_user(state_name, city, filename, account)
    except Exception as e:
        logging.error(f"Error reading CSV file: states/{state_name}.csv")
        print(f"Error reading CSV file: {e}")


def fetch_github_data_for_user(state, city, filename, username):
    try:
        url = f"https://api.github.com/users/{username}"
        time.sleep(3)
        initialResponse = requests.get(url)
        initialData = initialResponse.json()
        
        while 'login' not in initialData:
            logging.error("[USER-Initial] Exceed the github api limitiation")
            logging.error(json.dumps(initialData))
            time.sleep(600)
            initialResponse = requests.get(url)
            initialData = initialResponse.json()

        record = {
            'username': initialData['login'],
            'name': initialData['name'],
            'company': initialData['company'],
            'blog': initialData['blog'],
            'location': initialData['location'],
            'email': initialData['email'],
            'bio': initialData['bio'],
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
            'created_at': initialData['created_at']
        }

        url = f"https://api.github.com/users/{username}/social_accounts"

        time.sleep(3)
        socialResponse = requests.get(url)
        socialData = socialResponse.json()

        while not isinstance(socialData, list):
            logging.error("[USER-Social] Exceed the github api limitiation")
            logging.error(json.dumps(socialData))
            time.sleep(600)
            socialResponse = requests.get(url)
            socialData = socialResponse.json()

        for social in socialData:
            if(social['provider'] == 'generic'):
                record[social['provider']] += social['url'] + ', '
            else:
                 record[social['provider']] = social['url']

        record['generic'] = record['generic'][:-2]

        url = f"https://api.github.com/users/{username}/events/public"

        time.sleep(3)
        emailResponse = requests.get(url)
        emailData = emailResponse.json()

        while not isinstance(emailData, list):
            logging.error("[USER-Email] Exceed the github api limitiation")
            logging.error(json.dumps(emailData))
            time.sleep(600)
            emailResponse = requests.get(url)
            emailData = emailResponse.json()

        emailString = ""

        final=set()
        for x in emailData:
            if x['payload'].get('commits'):
                final.add(x['payload']['commits'][0]['author']['email'])
        for mail in final:
            emailString += mail + ', '

        record['email'] = emailString[:-2]
        write_user_data(state, city, filename, record)

    except Exception as e:
        logging.error(f"Error fetching GitHub data for {username}: {e}")
        print(f"Error fetching GitHub data for {username}: {e}")


def write_user_data(state, city, filename, record):
    state_path = os.path.join('users', state)
    city_path = os.path.join(state_path, city)
    file_path = os.path.join(city_path, filename)

    file_exists = os.path.isfile(file_path)

    print(record)

    df = pd.DataFrame([record])

    columns = [
        'username', 'name', 'company', 'blog', 'location', 'email', 'bio', 'facebook', 'instagram', 'linkedin',
        'npm', 'reddit', 'twitch', 'youtube', 'mastodon', 'hometown', 'twitter', 'generic', 'created_at'
    ]

    if file_exists:
        df.to_csv(file_path, mode='a', header=False, index=False, columns=columns, encoding='utf-8')
    else:
        df.to_csv(file_path, mode='w', header=True, index=False, columns=columns, encoding='utf-8')


def validate_date(date_str):
    try:
        parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
        formatted_date = parsed_date.strftime('%Y-%m-%d')
        return date_str == formatted_date
    except ValueError:
        return False


def validate_city(state, city):
    try:
        df = pd.read_csv(f"states/{state}.csv")
        if city in df['city_state_short'].values:
            return True
    except FileNotFoundError:
        print(f"CSV file for {state} not found.")
    return False


def main():
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

    # Start date input with validation
    while True:
        startDateInput = input("Enter Start Date (YYYY-MM-DD) or press Enter for '2014-01-01': ")
        if startDateInput == "":
            start_date = "2014-01-01"
            break
        elif validate_date(startDateInput):
            start_date = startDateInput
            break
        else:
            print("Invalid date format. Please enter the date in 'YYYY-MM-DD' format.")

    print("Start Date: ", start_date)

    # End date input with validation
    while True:
        endDateInput = input("Enter End Date (YYYY-MM-DD) or press Enter for '2023-12-31': ")
        if endDateInput == "":
            end_date = "2023-12-31"
            break
        elif validate_date(endDateInput):
            if datetime.strptime(start_date, '%Y-%m-%d') <= datetime.strptime(endDateInput, '%Y-%m-%d'):
                end_date = endDateInput
                break
            else:
                print("End date should be greater than or equal to start date.")
        else:
            print("Invalid date format. Please enter the date in 'YYYY-MM-DD' format.")

    print("End Date: ", end_date)

    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError as e:
        print(f"Error: {e}")
        return

    if state == "all":
        for state_name in states:
            fetch_github_accounts_from_state(state_name, start_date, end_date)
            fetch_github_users_from_state(state_name, start_date, end_date)
    else:
        if city == "all":
            fetch_github_accounts_from_state(state, start_date, end_date)
            fetch_github_users_from_state(state, start_date, end_date)
        else:
            fetch_github_accounts_from_city(state, city, start_date, end_date)
            fetch_github_users_from_city(state, city, start_date, end_date)


if __name__ == "__main__":
    main()