# This file containes code for data Scraping and further analysis

!pip install pandas requests tqdm

import requests
import pandas as pd
import time
from datetime import datetime
import os
from tqdm.notebook import tqdm

#users.csv
import requests
import csv

# Replace with your personal access token
GITHUB_TOKEN = 'TOKEN'
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}
BASE_URL = 'https://api.github.com'

def get_users_in_Melbourne():
    users = []
    page = 1

    while True:
        response = requests.get(f'{BASE_URL}/search/users',
                                headers=HEADERS,
                                params={'q': 'location:Melbourne followers:>100', 'page': page})
        data = response.json()

        if 'items' not in data or not data['items']:
            break

        for user in data['items']:
            users.append(user['login'])

        page += 1

    return users

def get_user_details(username):
    response = requests.get(f'{BASE_URL}/users/{username}', headers=HEADERS)
    return response.json()

def clean_company(company):
    if company:
        return company.strip().lstrip('@').upper()
    return None

def main():
    users = get_users_in_Melbourne()
    user_details = []

    for user in users:
        details = get_user_details(user)
        user_details.append({
            'login': details.get('login'),
            'name': details.get('name'),
            'company': clean_company(details.get('company')),
            'location': details.get('location'),
            'email': details.get('email'),
            'hireable': details.get('hireable'),
            'bio': details.get('bio'),
            'public_repos': details.get('public_repos'),
            'followers': details.get('followers'),
            'following': details.get('following'),
            'created_at': details.get('created_at'),
        })

    # Write to CSV
    with open('users.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['login', 'name', 'company', 'location', 'email',
                      'hireable', 'bio', 'public_repos', 'followers',
                      'following', 'created_at']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for user in user_details:
            writer.writerow(user)

if __name__ == '__main__':
    main()

#more cleaned users.csv
import pandas as pd

# Load the data
users_df = pd.read_csv('users.csv')

# Clean the company names
users_df['company'] = users_df['company'].str.strip()  # Trim whitespace
users_df['company'] = users_df['company'].str.lstrip('@')  # Strip leading '@'
users_df['company'] = users_df['company'].str.upper()  # Convert to uppercase

# Save the cleaned DataFrame back to users.csv
users_df.to_csv('users.csv', index=False)

print("Company names cleaned and saved to users.csv.")

#repositories.csv
import requests
import csv

# Replace with your personal access token
GITHUB_TOKEN = 'TOKEN'
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}
BASE_URL = 'https://api.github.com'

def read_users_from_csv(file_path):
    users = []
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            users.append(row['login'])
    return users

def get_repositories(username):
    repos = []
    page = 1
    while True:
        response = requests.get(f'{BASE_URL}/users/{username}/repos',
                                headers=HEADERS,
                                params={'sort': 'pushed', 'direction': 'desc', 'per_page': 100, 'page': page})
        data = response.json()

        if not data or len(repos) >= 500:
            break

        for repo in data:
            repos.append({
                'full_name': repo['full_name'],
                'created_at': repo['created_at'],
                'stargazers_count': repo['stargazers_count'],
                'watchers_count': repo['watchers_count'],
                'language': repo['language'],
                'has_projects': repo['has_projects'],
                'has_wiki': repo['has_wiki'],
                'license_name': repo['license']['key'] if repo.get('license') else None  # Safely fetch license key
            })

        page += 1

    return repos[:500]  # Return up to 500 repos

def main():
    users = read_users_from_csv('users.csv')
    all_repos = []

    for user in users:
        repos = get_repositories(user)
        for repo in repos:
            all_repos.append({
                'login': user,
                **repo
            })

    # Write to CSV
    with open('repositories.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['login', 'full_name', 'created_at',
                      'stargazers_count', 'watchers_count',
                      'language', 'has_projects',
                      'has_wiki', 'license_name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for repo in all_repos:
            writer.writerow(repo)

if __name__ == '__main__':
    main()

#Q1
import pandas as pd

# Load the data
users_df = pd.read_csv('users.csv')

# Sort by followers and get top 5
top_users = users_df.sort_values(by='followers', ascending=False).head(5)

# Extract logins
top_logins = top_users['login'].tolist()
result = ', '.join(top_logins)

print(result)

#Q2
import pandas as pd

# Load the data
users_df = pd.read_csv('users.csv')

# Convert created_at to datetime
users_df['created_at'] = pd.to_datetime(users_df['created_at'])

# Sort by created_at and get the earliest 5 users
earliest_users = users_df.sort_values(by='created_at').head(5)

# Extract logins
earliest_logins = earliest_users['login'].tolist()
result = ', '.join(earliest_logins)

print(result)

#Q3
import pandas as pd

# Load the data
repositories_df = pd.read_csv('repositories.csv')

# Filter out missing license names
repositories_df = repositories_df[repositories_df['license_name'].notna()]

# Count occurrences of each license
license_counts = repositories_df['license_name'].value_counts()

# Get the top 3 licenses
top_licenses = license_counts.head(3).index.tolist()

# Join the license names in order
result = ', '.join(top_licenses)

print(result)

#Q4
import pandas as pd

# Load the data
users_df = pd.read_csv('users.csv')

# Count occurrences of each company
company_counts = users_df['company'].value_counts()

# Get the company with the highest count
most_common_company = company_counts.idxmax()
most_common_count = company_counts.max()

print(f"The majority of developers work at: {most_common_company} with {most_common_count} developers.")

#Q5
import pandas as pd

# Load the data
repositories_df = pd.read_csv('repositories.csv')

# Count occurrences of each programming language, ignoring missing values
language_counts = repositories_df['language'].value_counts()

# Get the most popular programming language
most_popular_language = language_counts.idxmax()
most_popular_count = language_counts.max()

print(f"The most popular programming language is: {most_popular_language} with {most_popular_count} repositories.")

#Q6
import pandas as pd

# Load the data
users_df = pd.read_csv('users.csv')
repositories_df = pd.read_csv('repositories.csv')

# Convert created_at to datetime and filter users who joined after 2020
users_df['created_at'] = pd.to_datetime(users_df['created_at'])
recent_users = users_df[users_df['created_at'] > '2020-01-01']

# Get the logins of recent users
recent_user_logins = recent_users['login'].tolist()

# Filter repositories by these users
recent_repositories = repositories_df[repositories_df['login'].isin(recent_user_logins)]

# Count occurrences of each programming language
language_counts = recent_repositories['language'].value_counts()

# Get the second most popular programming language
second_most_popular_language = language_counts.nlargest(2).index[1]
second_most_popular_count = language_counts.nlargest(2).values[1]

print(f"The second most popular programming language among users who joined after 2020 is: {second_most_popular_language} with {second_most_popular_count} repositories.")

#Q7
import pandas as pd

# Load the data
repositories_df = pd.read_csv('repositories.csv')

# Group by programming language and calculate the average stars
average_stars = repositories_df.groupby('language')['stargazers_count'].mean()

# Identify the language with the highest average stars
highest_average_language = average_stars.idxmax()
highest_average_value = average_stars.max()

print(f"The programming language with the highest average number of stars per repository is: {highest_average_language} with an average of {highest_average_value:.2f} stars.")

#Q8
import pandas as pd

# Load the data
users_df = pd.read_csv('users.csv')

# Calculate leader_strength
users_df['leader_strength'] = users_df['followers'] / (1 + users_df['following'])

# Sort by leader_strength and get the top 5
top_leaders = users_df.sort_values(by='leader_strength', ascending=False).head(5)

# Extract logins
top_logins = top_leaders['login'].tolist()
result = ', '.join(top_logins)

print(result)

#Q9
import pandas as pd

# Load the data
users_df = pd.read_csv('users.csv')

# Calculate the correlation between followers and public repositories
correlation = users_df['followers'].corr(users_df['public_repos'])

print(f"The correlation between the number of followers and the number of public repositories is: {correlation:.3f}")

#Q10
import pandas as pd
import statsmodels.api as sm

# Load the data
users_df = pd.read_csv('users.csv')

# Define the independent variable (X) and dependent variable (Y)
X = users_df['public_repos']
Y = users_df['followers']

# Add a constant to the independent variable (for the intercept)
X = sm.add_constant(X)

# Fit the regression model
model = sm.OLS(Y, X).fit()

# Get the summary of the regression results
summary = model.summary()

# Extract the coefficient for public_repos
additional_followers_per_repo = model.params['public_repos']

print(f"Regression Results:\n{summary}")
print(f"Estimated additional followers per additional public repository: {additional_followers_per_repo:.3f}")

#Q11
import pandas as pd

# Load the data
repositories_df = pd.read_csv('repositories.csv')


# Calculate the correlation directly
correlation = repositories_df['has_projects'].astype(int).corr(repositories_df['has_wiki'].astype(int))

print(f"The correlation between having projects enabled and having a wiki enabled is: {correlation:.3f}")

#Q12
import pandas as pd

# Load the users data from the CSV file
users_df = pd.read_csv('users.csv')

# Filter hireable and non-hireable users
hireable_users = users_df[users_df['hireable'] == True]
non_hireable_users = users_df[users_df['hireable'].isna() | (users_df['hireable'] == False)]

# Calculate average following for both groups
average_hireable_following = hireable_users['following'].mean()
average_non_hireable_following = non_hireable_users['following'].mean()

# Calculate the difference
difference = average_hireable_following - average_non_hireable_following

# Print the result rounded to three decimal places
print(f'Difference in average following (hireable - non-hireable): {difference:.3f}')

if repos['has_projects'].dtype == 'object':
    repos['has_projects'] = repos['has_projects'].map({'true': True, 'false': False})
if repos['has_wiki'].dtype == 'object':
    repos['has_wiki'] = repos['has_wiki'].map({'true': True, 'false': False})

correlation = repos['has_projects'].corr(repos['has_wiki'])

print(round(correlation, 3))

#Q13
import pandas as pd
import statsmodels.api as sm

# Load the users data from the CSV file
users_df = pd.read_csv('users.csv')

# Filter out users without bios
users_with_bios = users_df[users_df['bio'].notna()]

# Calculate the length of the bio in words
#users_with_bios['bio_word_count'] = users_with_bios['bio'].str.split(" ").str.len()

users_with_bios['bio_word_count'] = users_with_bios['bio'].apply(lambda x: len(x.split()))


# Prepare the data for regression
X = users_with_bios['bio_word_count']  # Independent variable
y = users_with_bios['followers']        # Dependent variable

# Add a constant to the independent variable for the regression
X = sm.add_constant(X)

# Fit the regression model
model = sm.OLS(y, X).fit()

# Get the regression slope (coefficient for bio_word_count)
slope = model.params['bio_word_count']

# Print the slope rounded to three decimal places
print(f'Regression slope of followers on bio word count: {slope:.3f}')

#Q13
import pandas as pd
import statsmodels.api as sm

# Load the users data from the CSV file
users_df = pd.read_csv('users.csv')

# Filter out users without bios
users_with_bios = users_df[users_df['bio'].notna()]

# Calculate the length of the bio in words
#users_with_bios['bio_word_count'] = users_with_bios['bio'].str.split(" ").str.len()

users_with_bios['bio_word_count'] = users_with_bios['bio'].apply(lambda x: len(x.split()))


# Prepare the data for regression
X = users_with_bios['bio_word_count']  # Independent variable
y = users_with_bios['followers']        # Dependent variable

# Add a constant to the independent variable for the regression
X = sm.add_constant(X)

# Fit the regression model
model = sm.OLS(y, X).fit()

# Get the regression slope (coefficient for bio_word_count)
slope = model.params['bio_word_count']

# Print the slope rounded to three decimal places
print(f'Regression slope of followers on bio word count: {slope:.3f}')

users_df = pd.read_csv('users.csv')

# Check the data types and structure
print(users_df.head())

# Replace True/False with true/false in the hireable column
users_df['hireable'] = users_df['hireable'].replace({True: 'true', False: 'false'})

# Save the modified DataFrame back to the same CSV file
users_df.to_csv('users.csv', index=False)

# Check the data types and structure
print(users_df.head())


print("Updated CSV file saved successfully.")

repositories_df = pd.read_csv('repositories.csv')

# Check the data types and structure
print(repositories_df.head())

# Replace True/False with true/false
repositories_df['has_projects'] = repositories_df['has_projects'].replace({True: 'true', False: 'false'})
repositories_df['has_wiki'] = repositories_df['has_wiki'].replace({True: 'true', False: 'false'})

# Save the modified DataFrame back to the same CSV file
repositories_df.to_csv('repositories.csv', index=False)

# Check the data types and structure
print(repositories_df.head())

print("Updated CSV file saved successfully.")

#Q16
import pandas as pd

# Load the users data from the CSV file
users_df = pd.read_csv('users.csv')

# Filter out users without names
valid_users = users_df[users_df['name'].notna()]

# Extract surnames (last word in name)
valid_users['surname'] = valid_users['name'].str.strip().str.split().str[-1]

# Count occurrences of each surname
surname_counts = valid_users['surname'].value_counts()

# Find the most common surname(s)
max_count = surname_counts.max()
most_common_surnames = surname_counts[surname_counts == max_count].index.tolist()

# Sort surnames alphabetically
most_common_surnames.sort()

# Count users with the most common surname
number_of_users = max_count

# Print results
most_common_surnames_str = ', '.join(most_common_surnames)
print(f'Most common surname(s): {most_common_surnames_str}')
print(f'Number of users with the most common surname: {number_of_users}')

#Q15
import pandas as pd

# Load the users data from the CSV file
users_df = pd.read_csv('users.csv')

# Total number of users
total_users = len(users_df)

# Filter hireable and non-hireable users
hireable_users = users_df[users_df['hireable'] == True]
non_hireable_users = users_df[users_df['hireable'].isna() | (users_df['hireable'] == False)]

# Calculate the fraction of users with email in both groups
fraction_hireable_with_email = hireable_users['email'].notna().mean()
fraction_non_hireable_with_email = non_hireable_users['email'].notna().mean()

# Calculate the difference
difference = fraction_hireable_with_email - fraction_non_hireable_with_email

# Print the result rounded to three decimal places
print(f'Difference in fraction of users with email: {difference:.3f}')

#Q14
import pandas as pd

# Load the repositories data from the CSV file
repos_df = pd.read_csv('repositories.csv')

# Convert the created_at column to datetime
repos_df['created_at'] = pd.to_datetime(repos_df['created_at'])

# Filter for weekend days (Saturday: 5, Sunday: 6)
weekend_repos = repos_df[repos_df['created_at'].dt.dayofweek.isin([5, 6])]

# Count the number of repositories created by each user
top_users = weekend_repos['login'].value_counts().head(5)

# Get the top 5 users' logins in order
top_users_logins = ', '.join(top_users.index)

# Print the result
print(f'Top 5 users who created the most repositories on weekends: {top_users_logins}')
