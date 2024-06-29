import pandas as pd
import requests
import csv
from datetime import datetime, timedelta
import time
import os
import argparse

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


def process_cities_from_csv(state_name, start_date, end_date):

    file_path = 'states/'+state_name+'.csv'
    try:
        df = pd.read_csv(file_path)
        cities = df['city_state_short'].dropna().str.strip().tolist()
        os.makedirs('username/'+state_name, exist_ok=True)
        for city in cities:
            fetch_github_users_for_all_dates(state_name, city, start_date, end_date)
    except Exception as e:
        print(f"Error reading CSV file: {e}")

def fetch_github_users_for_all_dates(state, city, start_date, end_date):
    current_date = start_date

    while current_date <= end_date:
        fetch_github_users(state, city, current_date)
        current_date = current_date + timedelta(days=31) 

def fetch_github_users(state, city, current_date, page=1):
    try:
        from_date = current_date.strftime('%Y-%m-%d')
        to_date = (current_date + timedelta(days=30)).strftime('%Y-%m-%d')
        per_page = 100
        url = f"https://api.github.com/search/users?q=created:{from_date}..{to_date} location:\"{city}\" type:user&per_page={per_page}&page={page}"
        
        time.sleep(3)
        response = requests.get(url)
        data = response.json()

        records = [{
            'username': item['login'],
            'User ID': item['id'],
            'Profile URL': item['html_url'],
        } for item in data.get('items', [])]

        write_username_data(state, current_date.year, current_date.month, city,  records)

        total_count = data.get('total_count', 0)
        if page * per_page < total_count:
            fetch_github_users(state, city, current_date, page + 1)
    except Exception as e:
        print(f"Error fetching GitHub data for {city}: {e}")

def write_username_data(state, year, month, city, records):
    file_path = 'username/' + state + '/'+ str(year) + '.' + str(month) + '.csv'
    file_exists = os.path.isfile(file_path)

    print(state, city, str(year) + '.' + str(month), len(records) )

    with open(file_path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['username', 'User ID', 'Profile URL'])
        
        if not file_exists:
            writer.writeheader()

        for record in records:
            writer.writerow(record)


def process_usernames_from_csv(state, start_date, end_date):
    current_date = start_date

    while current_date <= end_date:
        file_path = 'username/'+ state + '/' + str(current_date.year) + '.' + str(current_date.month) +'.csv'
        try:
            df = pd.read_csv(file_path)
            usernames = df['username'].dropna().str.strip().tolist()
            os.makedirs('result/'+state, exist_ok=True)
            for username in usernames:
                fetch_github_data_for_user(state, str(current_date.year) + '.' + str(current_date.month), username)
        except Exception as e:
            print(f"Error reading CSV file: {e}")
        current_date = current_date + timedelta(days=31) 

def fetch_github_data_for_user(state, filename, username):
    try:
        url = f"https://api.github.com/users/{username}"
        
        time.sleep(4)
        initialResponse = requests.get(url)
        initialData = initialResponse.json()
        print(initialData)

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

        time.sleep(4)
        socialResponse = requests.get(url)
        socialData = socialResponse.json()

        for social in socialData:
            if(social['provider'] == 'generic'):
                record[social['provider']] += social['url'] + ', '
            else:
                 record[social['provider']] = social['url']

        record['generic'] = record['generic'][:-2]

        url = f"https://api.github.com/users/{username}/events/public"

        time.sleep(4)
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

        write_all_data(state, filename, record)

    except Exception as e:
        print(f"Error fetching GitHub data for {username}: {e}")

def write_all_data(state, filename, record):
    file_path = 'result/' + state + '/'+ filename + '.csv'
    file_exists = os.path.isfile(file_path)

    print(record)

    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'username', 'name', 'company', 'blog', 'location', 'email', 'bio', 'facebook', 'instagram', 'linkedin'
            , 'npm', 'reddit', 'twitch', 'youtube', 'mastodon', 'hometown', 'twitter', 'generic', 'created_at'])
        
        if not file_exists:
            writer.writeheader()

        writer.writerow(record)

def get_all_file_names(directory):
    try:
        file_names = os.listdir(directory)
        files = [f for f in file_names if os.path.isfile(os.path.join(directory, f))]
        return files
    except Exception as e:
        print(f"Error: {e}")
        return []

def main():

    stateInput = input("Enter State Name: ")
    state = stateInput if stateInput!="" else "all"
    print("State: ", state)

    startDateInput = input("Enter Start Date (YYYY-MM-DD): ")
    start_date = startDateInput if startDateInput!="" else "2014-01-01"
    print("Start Date: ", start_date)

    endDateInput = input("Enter End Date (YYYY-MM-DD): ")
    end_date = endDateInput if endDateInput!="" else "2023-12-31"
    print("End Date: ", end_date)

    cityInput = input("Enter City Name: ")
    city = cityInput if cityInput!="" else "all"
    print("City Name: ", city)

    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    if state == "all" :
        for state_name in states:
            if city == "all":
                process_cities_from_csv(state_name, start_date, end_date)
            else :
                fetch_github_users_for_all_dates(state_name, city, start_date, end_date)
            process_usernames_from_csv(state_name, start_date, end_date)
    else:
        if city == "all":
            process_cities_from_csv(state, start_date, end_date)
        else :
            fetch_github_users_for_all_dates(state, city, start_date, end_date)
        process_usernames_from_csv(state, start_date, end_date)

if __name__ == "__main__":
    main()