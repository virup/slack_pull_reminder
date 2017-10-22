import os
import sys
import datetime
import pytz
import json
import re
import mechanize
import cookielib

import requests
from github3 import login
from slackclient import SlackClient

POST_URL = 'https://slack.com/api/chat.postMessage'

ignore = os.environ.get('IGNORE_WORDS')
IGNORE_WORDS = ignore.split(',') if ignore else []
SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL', '#test')
REMINDER_DAYS = os.environ.get('REMINDER_DAYS', 2)

try:
    SLACK_API_TOKEN = os.environ['SLACK_API_TOKEN']
    GITHUB_API_TOKEN = os.environ['GITHUB_API_TOKEN']
    organization_string = os.environ['ORGANIZATION']
    ORGANIZATIONS = organization_string.split(',')
except KeyError as error:
    sys.stderr.write('Please set the environment variable {0}'.format(error))
    sys.exit(1)


def get_message(title, text, color):
    json_map = {}
    json_map['text'] = text
    json_map['pretext'] = title
    json_map['fallback'] = text
    json_map['color'] = color
    json_map['mrkdwn_in'] = ["text", "pretext"]
    return "[" + json.dumps(json_map) + "]"

def fetch_repository_pulls(repository):
    return [pull for pull in repository.pull_requests()
            if pull.state == 'open']

def is_valid_title(title):
    lowercase_title = title.lower()
    for ignored_word in IGNORE_WORDS:
        if ignored_word.lower() in lowercase_title:
            return False

    return True


def format_pull_requests(pull_requests, owner, repository):
    lines = []

    for pull in pull_requests:
        if is_valid_title(pull.title):
            no_activity_for_days = (datetime.datetime.now().replace(tzinfo=pytz.timezone("GMT")) - pull.updated_at).days
            if no_activity_for_days < 2:
                # Find if this review has been out for a long time
                pr_is_out_for_days = (datetime.datetime.now().replace(tzinfo=pytz.timezone("GMT")) - pull.created_at).days
                if pr_is_out_for_days < 5:
                    # No need to complain about it yet
                    continue
            creator = pull.user.login
            msg_format_with_elipse = '*[{1}]* <{2}|{3}...> - by {4}'
            msg_format_without_elipse = '*[{1}]* <{2}|{3}> - by {4}'

            msg_format = msg_format_without_elipse
            if len(pull.title) > 40:
                msg_format = msg_format_with_elipse

            line = msg_format.format(owner, repository, pull.html_url, pull.title[:45], creator.split("-")[0])

            lines.append(line + "\n")

    return lines


def fetch_organization_pulls(organization_name):
    """
    Returns a formatted string list of open pull request messages.
    """
    client = login(token=GITHUB_API_TOKEN)
    organization = client.organization(organization_name)
    lines = []

    for repository in organization.repositories():
        unchecked_pulls = fetch_repository_pulls(repository)
        lines += format_pull_requests(unchecked_pulls, organization_name,
                                      repository.name)

    return lines


def send_to_slack(text):
    payload = {
        'token': SLACK_API_TOKEN,
        'channel': SLACK_CHANNEL,
        'username': 'Pull Request Reminder',
        'icon_emoji': ':bell:',
        'text': text
    }

    response = requests.post(POST_URL, data=payload)
    answer = response.json()
    if not answer['ok']:
        raise Exception(answer['error'])

def send_to_slack2(org, text):
    sc = SlackClient(SLACK_API_TOKEN)

    line = get_message("ARGH! These reviews have not been updated in the last {0} days in *{1}* repo".format(REMINDER_DAYS, org), text, "#ff0000")

    sc.api_call(
        "chat.postMessage",
        username='Pull Request Reminder',
        icon_emoji=':bell:',
        channel=SLACK_CHANNEL,
        attachments=line
    )


def cli():
    for org in ORGANIZATIONS:
        pulls_for_org = fetch_organization_pulls(org)

        if pulls_for_org:
            send_to_slack2(org, ''.join(pulls_for_org))

def lambda_handler(event, context):
	cli()

if __name__ == '__main__':
    cli()
