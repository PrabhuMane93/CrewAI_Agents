from langgraph.graph import StateGraph

from langchain_community.tools.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)

credentials = get_gmail_credentials(
    token_file="token.json",
    scopes=["https://mail.google.com/"],
    client_secrets_file="credentials.json",
)
api_resource = build_resource_service(credentials=credentials)

from agents import EmailFilterCrew

import datetime
from typing import TypedDict

class EmailsState(TypedDict):
	checked_emails_ids: list[str]
	emails: list[dict]
	action_required_emails: dict

import os
import time

from langchain_community.agent_toolkits import GmailToolkit
from langchain_community.tools.gmail.search import GmailSearch

class Nodes():
	def __init__(self):
		self.gmail = GmailToolkit(api_resource=api_resource)

	def check_email(self, state):
		print("# Checking for new emails")
		search = GmailSearch(api_resource=self.gmail.api_resource)
		emails = search('after:newer_than:1d')
		checked_emails = state['checked_emails_ids'] if state['checked_emails_ids'] else []
		thread = []
		new_emails = []
		for email in emails:
			if (email['id'] not in checked_emails) and (email['threadId'] not in thread) and ( os.environ['MY_EMAIL'] not in email['sender']):
				thread.append(email['threadId'])
				new_emails.append(
					{
						"id": email['id'],
						"threadId": email['threadId'],
						"snippet": email['snippet'],
						"sender": email["sender"]
					}
				)
		checked_emails.extend([email['id'] for email in emails])
		return {
			**state,
			"emails": new_emails,
			"checked_emails_ids": checked_emails
		}

	def wait_next_run(self, state):
		print("## Waiting for 180 seconds")
		time.sleep(180)
		return state

	def new_emails(self, state):
		if len(state['emails']) == 0:
			print("## No new emails")
			return "end"
		else:
			print("## New emails")
			return "continue"


class WorkFlow():
	def __init__(self):
		nodes = Nodes()
		workflow = StateGraph(EmailsState)

		workflow.add_node("check_new_emails", nodes.check_email)
		workflow.add_node("wait_next_run", nodes.wait_next_run)
		workflow.add_node("draft_responses", EmailFilterCrew().kickoff)

		workflow.set_entry_point("check_new_emails")
		workflow.add_conditional_edges(
				"check_new_emails",
				nodes.new_emails,
				{
					"continue": 'draft_responses',
					"end": 'wait_next_run'
				}
		)
		workflow.add_edge('draft_responses', 'wait_next_run')
		workflow.add_edge('wait_next_run', 'check_new_emails')
		self.app = workflow.compile()