import os
import requests
from dotenv import load_dotenv


def main():

    # Get workspaces
    workspaces = get_asana_workspaces()
    projects = get_asana_projects(workspaces)
    webhooks = get_asana_webhooks(workspaces)

    # Delete original webhooks
    delete_webhooks(webhooks)

    # Get new webhooks
    interested = os.getenv('ASANA_INTERESTED').split(';')
    projects = filter(lambda project: project['name'] in interested, projects)
    add_webhooks(projects)


def get_asana_workspaces():

    # Set up request
    workspaceUrl = 'https://app.asana.com/api/1.0/users/me/workspaces'
    headers = {'Authorization': 'Bearer {}'.format(os.getenv('ASANA_TOKEN'))}

    # Get workspaces
    workspaces = requests.get(workspaceUrl, headers=headers).json()['data']
    print('Found %s Asana workspaces' % len(workspaces))

    return workspaces


def get_asana_projects(workspaces):

    projects = []
    for workspace in workspaces:
        projectUrl = 'https://app.asana.com/api/1.0/workspaces/{}/projects'.format(workspace['gid'])
        headers = {'Authorization': 'Bearer {}'.format(os.getenv('ASANA_TOKEN'))}
        projects.extend(requests.get(projectUrl, headers=headers).json()['data'])

    print('Found %s Asana projects' % len(projects))
    return projects


def get_asana_webhooks(workspaces):

    # Query for webhooks from all workspaces
    webhooks = []
    for workspace in workspaces:
        webhookUrl = 'https://app.asana.com/api/1.0/webhooks'
        params = {'workspace': workspace['gid']}
        headers = {'Authorization': 'Bearer {}'.format(os.getenv('ASANA_TOKEN'))}
        webhooks.extend(requests.get(webhookUrl, params=params, headers=headers).json()['data'])

    print('Found %s Asana webhooks' % len(webhooks))
    return webhooks


def delete_webhooks(webhooks):

    for webhook in webhooks:
        webhookUrl = 'https://app.asana.com/api/1.0/webhooks/' + webhook['gid']
        headers = {'Authorization': 'Bearer {}'.format(os.getenv('ASANA_TOKEN'))}
        if requests.delete(webhookUrl, headers=headers).ok:
            resource = webhook['resource']
            print('Deleted webhook for %s %s' % (resource['resource_type'], resource['name']))
        else:
            print('Failure deleting webhook %s' % webhook['gid'])


def add_webhooks(projects):

    for project in projects:

        # Set up variables
        webhookUrl = 'https://app.asana.com/api/1.0/webhooks'
        headers = {'Authorization': 'Bearer {}'.format(os.getenv('ASANA_TOKEN'))}
        data = {
            'resource': project['gid'],
            'target': os.getenv('ASANA_TARGET')
        }

        # Do request
        result = requests.post(webhookUrl, data=data, headers=headers)
        if result.ok:
            resource = result.json()['data']['resource']
            print('Created webhook for %s %s' % (resource['resource_type'], resource['name']))
        else:
            print('Failure creating webhook for %s %s due to %s' %
                  (project['name'], project['gid'], result.reason))


if __name__ == '__main__':

    # Load .env file
    load_dotenv()

    # Run main
    main()
