from langchain_community.agent_toolkits import GmailToolkit
from langchain_community.tools.gmail.get_thread import GmailGetThread
from langchain_community.tools.tavily_search import TavilySearchResults

from textwrap import dedent
from crewai import Agent

from langchain_community.agent_toolkits import GmailToolkit
from langchain_community.tools.gmail.create_draft import GmailCreateDraft
from langchain.tools import tool

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

class CreateDraftTool():
  @tool("Create Draft")
  def create_draft(data):
    """
    	Useful to create an email draft.
      The input to this tool should be a pipe (|) separated text
      of length 3 (three), representing who to send the email to,
      the subject of the email and the actual message.
      For example, `lorem@ipsum.com|Nice To Meet You|Hey it was great to meet you.`.
    """
    email, subject, message = data.split('|')
    gmail = GmailToolkit(api_resource=api_resource)
    draft = GmailCreateDraft(api_resource=gmail.api_resource)
    resutl = draft({
				'to': [email],
				'subject': subject,
				'message': message
		})
    return f"\nDraft created: {resutl}\n"

class EmailFilterAgents():
	def __init__(self):
		self.gmail = GmailToolkit(api_resource=api_resource)

	def email_filter_agent(self):
		return Agent(
			role='Senior Email Analyst',
			goal='Filter out non-essential emails like newsletters and promotional content',
			backstory=dedent("""\
				As a Senior Email Analyst, you have extensive experience in email content analysis.
				You are adept at distinguishing important emails from spam, newsletters, and other
				irrelevant content. Your expertise lies in identifying key patterns and markers that
				signify the importance of an email."""),
			verbose=True,
			allow_delegation=False
		)

	def email_action_agent(self):

		return Agent(
			role='Email Action Specialist',
			goal='Identify action-required emails and compile a list of their IDs',
			backstory=dedent("""\
				With a keen eye for detail and a knack for understanding context, you specialize
				in identifying emails that require immediate action. Your skill set includes interpreting
				the urgency and importance of an email based on its content and context."""),
			tools=[
				GmailGetThread(api_resource=self.gmail.api_resource),
				TavilySearchResults()
			],
			verbose=True,
			allow_delegation=False,
		)

	def email_response_writer(self):
		return Agent(
			role='Email Response Writer',
			goal='Draft responses to action-required emails',
			backstory=dedent("""\
				You are a skilled writer, adept at crafting clear, concise, and effective email responses.
				Your strength lies in your ability to communicate effectively, ensuring that each response is
				tailored to address the specific needs and context of the email."""),
			tools=[
				TavilySearchResults(),
				GmailGetThread(api_resource=self.gmail.api_resource),
				CreateDraftTool.create_draft
			],
			verbose=True,
			allow_delegation=False,
		)
	

from crewai import Crew

from crewai import Task
from textwrap import dedent

class EmailFilterTasks:
	def filter_emails_task(self, agent, emails):
		return Task(
			description=dedent(f"""\
				Analyze a batch of emails and filter out
				non-essential ones such as newsletters, promotional content and notifications.

			  Use your expertise in email content analysis to distinguish
				important emails from the rest, pay attention to the sender and avoind invalid emails.

				Make sure to filter for the messages actually directed at the user and avoid notifications.

				EMAILS
				-------
				{emails}

				Your final answer MUST be a the relevant thread_ids and the sender, use bullet points.
				"""),
			agent=agent
		)

	def action_required_emails_task(self, agent):
		return Task(
			description=dedent("""\
				For each email thread, pull and analyze the complete threads using only the actual Thread ID.
				understand the context, key points, and the overall sentiment
				of the conversation.

				Identify the main query or concerns that needs to be
				addressed in the response for each

				Your final answer MUST be a list for all emails with:
				- the thread_id
				- a summary of the email thread
				- a highlighting with the main points
				- identify the user and who he will be answering to
				- communication style in the thread
				- the sender's email address
				"""),
			agent=agent
		)

	def draft_responses_task(self, agent):
		return Task(
			description=dedent(f"""\
				Based on the action-required emails identified, draft responses for each.
				Ensure that each response is tailored to address the specific needs
				and context outlined in the email.

				- Assume the persona of the user and mimic the communication style in the thread.
				- Feel free to do research on the topic to provide a more detailed response, IF NECESSARY.
				- IF a research is necessary do it BEFORE drafting the response.
				- If you need to pull the thread again do it using only the actual Thread ID.

				Use the tool provided to draft each of the responses.
				When using the tool pass the following input:
				- to (sender to be responded)
				- subject
				- message

				You MUST create all drafts before sending your final answer.
				Your final answer MUST be a confirmation that all responses have been drafted.
				"""),
			agent=agent
		)

class EmailFilterCrew():
	def __init__(self):
		agents = EmailFilterAgents()
		self.filter_agent = agents.email_filter_agent()
		self.action_agent = agents.email_action_agent()
		self.writer_agent = agents.email_response_writer()

	def kickoff(self, state):
		print("### Filtering emails")
		tasks = EmailFilterTasks()
		crew = Crew(
			agents=[self.filter_agent, self.action_agent, self.writer_agent],
			tasks=[
				tasks.filter_emails_task(self.filter_agent, self._format_emails(state['emails'])),
				tasks.action_required_emails_task(self.action_agent),
				tasks.draft_responses_task(self.writer_agent)
			],
			verbose=True
		)
		result = crew.kickoff()
		return {**state, "action_required_emails": result}

	def _format_emails(self, emails):
		emails_string = []
		for email in emails:
			print(email)
			arr = [
				f"ID: {email['id']}",
				f"- Thread ID: {email['threadId']}",
				f"- Snippet: {email['snippet']}",
				f"- From: {email['sender']}",
				f"--------"
			]
			emails_string.append("\n".join(arr))
		return "\n".join(emails_string)