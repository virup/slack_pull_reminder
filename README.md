# Slack pull reminder

This program computes the pull requests in github.com which have not been updated for some (configurable) days and posts the list on one of your your organization's slack channel. This also creates a zip file which can be directly uploaded and used as AWS lambda. 

## Run

### Set the following environment variables
	- SLACK_CHANNEL: The slack channel to post the pull request list
	- REMINDER_DAYS: The number of days for which the pull request has not been updated
	- SLACK_API_TOKEN: Your slack api token
	- GITHUB_API_TOKEN: The github api token
	- ORGANIZATION: Comma separated list of github organizations you want this program to run 

### Run locally
	- python slack_pull_reminder/slack_pull_reminder.py

### Run as AWS lambda
	- make build
	- upload the zip under 'packages' directory

## Prerequisites

- Install the following:  
	-- pip install pytz  
	-- pip install mechanize  
	-- pip install github3.py  	
	-- pip install slackclient


- Build the product:  
	-- make build
	The zip file to be uploaded for AWS lambda is located in the 'packages' directory

- Clean 
	-- make clean_package


