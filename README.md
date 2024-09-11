# GitHub User Information Fetcher

This project fetches user information from GitHub's public API based on specified states, cities, and date ranges. It retrieves user profiles and their social accounts, and it saves this data into CSV files.

## Table of Contents
 
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Github public APIs used in this project](#github-public-apis-used-in-this-project)
- [Logging](#logging)
- [API Rate Limiting](#api-rate-limiting)
- [Contributing](#contributing)

## Prerequisites

Ensure you have the following installed on your machine:

- Python 3.12.4
- `pip` (Python package installer)
- `virtualenv` (optional but recommended)

## Installation

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/yourusername/github-user-fetcher.git
    cd github-user-fetcher
    ```

2. **Create a Virtual Environment** (optional but recommended):
    ```sh
    python -m venv venv
    ```

3. **Activate the Virtual Environment**:

    - On Windows:
        ```sh
        venv\Scripts\activate
        ```
    - On macOS/Linux:
        ```sh
        source venv/bin/activate
        ```

4. **Install Required Packages**:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. **Run the Script**:
    ```sh
    python main.py
    ```

2. **Input Prompts**:
    - **State Name**: Enter the name of the state or press Enter for 'all'.
    - **City Name**: Enter the name of the city or press Enter for 'all'.
    - **Start Date**: Enter the start date in `YYYY-MM-DD` format or press Enter for '2014-01-01'.
    - **End Date**: Enter the end date in `YYYY-MM-DD` format or press Enter for '2023-12-31'.

    The script will fetch GitHub user data based on the provided inputs and save it into CSV files.

## Project Structure

- `main.py`: Main script that contains the logic to fetch and save GitHub user data.
- `states/`: Directory containing CSV files for each state with city information.
- `accounts/`: Directory where fetched account data will be saved.
- `users/`: Directory where fetched user data will be saved.
- `error.log`: Log file for capturing errors.

## Github public APIs used in this project
- get user list by location, created date, type <br/>
`https://api.github.com/search/users?q=created:{start_date}..{end_date} location:"{city}" type:user&per_page={per_page}&page={page}`
- get user initial information by username <br/>
`https://api.github.com/users/{username}`
- get user social information by username <br/>
`https://api.github.com/users/{username}/social_accounts`
- get user email information by username <br/>
`https://api.github.com/users/{username}/events/public`


## Logging

Errors encountered during execution are logged in `error.log`. You can review this file to debug issues.

## API Rate Limiting

The script includes logic to handle GitHub API rate limiting by pausing execution and retrying requests when the rate limit is exceeded.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

