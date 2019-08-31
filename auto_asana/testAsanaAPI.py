import os
import requests
from dotenv import load_dotenv


def get_workspaces():

    url = 'https://app.asana.com/api/1.0/users/me/workspaces'
    headers = {'Authorization': 'Bearer {}'.format(os.getenv('TOKEN'))}

    data = requests.get(url, headers=headers).json()
    return data['data']


def get_projects(workspace):

    url = 'https://app.asana.com/api/1.0/workspaces/{}/projects'.format(workspace)
    headers = {'Authorization': 'Bearer {}'.format(os.getenv('TOKEN'))}

    data = requests.get(url, headers=headers).json()
    return data['data']


def get_tasks(project):

    url = 'https://app.asana.com/api/1.0/projects/{}/tasks'.format(project)
    headers = {'Authorization': 'Bearer {}'.format(os.getenv('TOKEN'))}

    data = requests.get(url, headers=headers).json()
    return data['data']

"""
Main
"""
# Load environment variables
load_dotenv()

# Print all projects
workspaces = get_workspaces()
projects = [project for workspace in workspaces for project in get_projects(workspace['id'])]
for project in projects:
    print(project)

# Assign task to self
url = 'https://app.asana.com/api/1.0/tasks/{}'.format(os.getenv('TEST_TASK'))
data = {'assignee': 'me'}
headers = {'Authorization': 'Bearer {}'.format(os.getenv('TOKEN'))}

data = requests.put(url, data=data, headers=headers).json()
print(data)
