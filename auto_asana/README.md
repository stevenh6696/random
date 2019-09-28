# Webhook server

Webhook server hosted on free tier of Azure to automate some stuff

## Azure setup

Free tier on Azure to run the server.

### Steps

1. Go to [Azure portal](https://portal.azure.com/#home)
2. Create a new web app, creating app service plan and subscription if needed
   - Free tier should be enough for own usage
3. Set up deployment to push code to the app service
4. Set up configuration to save environment variables

## Asana self assign

Assign newly created tasks to self.

### Steps

1. [Get personal access token](https://asana.com/developers/documentation/getting-started/auth#personal-access-token) from asana to do all tasks on behalf of self
2. [Create webhook](https://asana.com/developers/api-reference/webhooks#create) with target as endpoint on server
3. Parse webhook events for newly created events
4. [Update the task](https://asana.com/developers/api-reference/tasks#update) and assign to self using parsed task GID

## Asana upcoming

Move tasks from other sections to "upcoming" section on kanban according to due date.

### Steps

1. [Get personal access token](https://asana.com/developers/documentation/getting-started/auth#personal-access-token) from asana to do all tasks on behalf of self
2. Query for [tasks in a section](https://asana.com/developers/api-reference/tasks#query)
   - Premium users are able to perform more refined queries
3. [Get more information](https://asana.com/developers/api-reference/tasks#get) about each task
4. Parse for events due less than a week later
5. [Move the tasks](https://asana.com/developers/api-reference/tasks#projects) to a new section

## Facebook interested events calendar

Put all events marked interested or attending on facebook to a google calendar.

### Facebook steps

1. [Create new app](https://developers.facebook.com/) as a facebook developer
2. [Get user token](https://developers.facebook.com/tools/accesstoken/) and authorize app to access account
   - Cannot find a way now to automatically refresh the token, so expires every 2 months
3. [Create webhook](https://developers.facebook.com/docs/graph-api/reference/v4.0/app/subscriptions) with {"object": "user"} and {"fields": "events"} to get event-related updates
4. Parse webhook events for interested events
5. [Query for more information](https://developers.facebook.com/docs/graph-api/reference/event/) about the given event ID using the user token

### Google steps

1. [Create a project](https://console.developers.google.com) to use google APIs
2. Enable google calendar API for the project from Project-Page &rarr; Library
3. Create a bot account for the project from Project-Page &rarr; Credentials
4. Share a calendar with the bot account
5. Download bot account credentials (Should be similar to the client configuration from [the quickstart](https://developers.google.com/calendar/quickstart/python))
6. [Add events](https://developers.google.com/calendar/v3/reference/events/insert) to the calendar using the bot credentials and information from facebook event
