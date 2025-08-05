import os
os.environ["OPENAI_API_KEY"] = "API_KEY_HERE"

from crewai import Agent
from langchain_community.llms import Ollama

#Our model library
# coding_model = Ollama(model="deepseek-coder:33b-instruct-q4_K_M")
# writing_model = Ollama(model="starling-lm:7b-alpha-q4_K_M")
# instruction_model = Ollama(model="alfred:40b-1023-q4_1")
# general_purpose_model = Ollama(model="nous-hermes2-mixtral:8x7b-dpo-q4_K_M")
# math_and_science_model = Ollama(model="wizard-math:70b-q4_K_M")
# dumb_and_fast_model = Ollama(model="orca-mini:latest")
# multimodal_model = Ollama(model="llava:latest")
# function_calling_model = Ollama(model="calebfahlgren/natural-functions:Q8_0")

# overseer_model_goliath = Ollama(model="goliath:120b-q4_K_M")
# overseer_model_qwen = Ollama(model="qwen:72b")
# summarizer_model = Ollama(model="eas/capybara-tess-yi-34b-200k-dare-ties:q4_0-4k")

from apitest import CustomLLM

api_endpoint = "https://dev.katonic.ai/65effc5e1b2244c08d1239ee/genai/gd-d5b452d8-1c78-4010-9de1-72dde384090c/api/v1/predict"

katonic_llm = CustomLLM(api_endpoint= api_endpoint)


#Tools we'll be using
from langchain_community.tools import DuckDuckGoSearchRun
#from langchain_community.tools import WikipediaQueryRun
from langchain.agents import load_tools
search_tool = DuckDuckGoSearchRun()
#wiki_tool = WikipediaQueryRun()
human_tool = load_tools(["human"])


# Topic that will be used in the crew run
topic = 'Generate a crewAI logic structure that is adept at breaking down large tasks, and running for X amount of time to generate a solution, and iteratively improve it.  '

summarizer = Agent(
    role='Office Historian',
    goal='Provide accurate, helpful, and concise summaries of large blocks of text for other agents to use',
    verbose=True,
    backstory="Expert at accurately and succinctly capturing the relevant details of text. This agent can help reduce huge amounts of tokens to smaller, more meaningful text blocks for other agents."
)

# Agent optimized for coding tasks - Task Decomposer
coder = Agent(
  role='Software Developer',
  goal='Decompose large tasks into actionable subtasks.',
  verbose=True,
  backstory="Expert at breaking down complex problems into manageable steps, this agent uses coding prowess to outline clear, executable subtasks from overarching objectives.",
  # llm=coding_model,
  llm = katonic_llm,
  allow_delegation=True,
)

# General purpose agent - Time Manager
generalist = Agent(
  role='Jack of All Trades',
  goal='Ensure solutions are generated and delivered on time.',
  verbose=True,
  backstory="With a versatile skill set, this agent excels at keeping projects on schedule, ensuring that every phase of the task meets its deadlines without sacrificing quality.",
  # llm=general_purpose_model,
  llm = katonic_llm,
  allow_delegation=True,
)

# Agent optimized for interpreting instructions - Solution Developer
instructor = Agent(
  role='Instructional Designer',
  goal='Generate effective solutions for subtasks.',
  verbose=True,
  backstory="Skilled in interpreting complex instructions, this agent crafts detailed, actionable solutions that address each decomposed subtask with precision and clarity.",
  # llm=instruction_model,
  llm = katonic_llm,
  allow_delegation=False,
)

# Agent optimized for writing tasks - Documentation Specialist
writer = Agent(
  role='Content Writer',
  goal='Document solutions and processes clearly.',
  verbose=True,
  backstory="A master of words, this agent is tasked with articulating the processes and solutions developed, ensuring clear documentation and communication of the project's progress.",
  # llm=writing_model,
  llm = katonic_llm,
  allow_delegation=False,
)

# Agent specialized in math and science - Solution Optimizer
math_scientist = Agent(
  role='Mathematician/Scientist',
  goal='Iteratively improve solutions for increased efficacy.',
  verbose=True,
  backstory="Utilizing a deep understanding of mathematics and science, this agent analyzes solutions to identify improvements, optimizing the project's outcomes through rigorous evaluation.",
  # llm=math_and_science_model,
  llm = katonic_llm,
  allow_delegation=False,
)

# Oversight agent with broad capabilities (Goliath) - Project Overseer
# overseer_goliath = Agent(
#   role='Project Manager',
#   goal='Coordinate efforts for cohesive progress and solution integration.',
#   verbose=True,
#   backstory="This agent oversees the entire operation, ensuring that all agents work cohesively towards the goal. It facilitates communication and integration between the different stages of the task, guiding the project to success.",
#   llm=overseer_model_goliath,
#   allow_delegation=True,
# )

# Oversight agent with broad capabilities - Project Overseer
overseer_qwen = Agent(
  role='Operations Director',
  goal='Coordinate the efforts of all agents to ensure cohesive progress and integration of solutions.',
  verbose=True,
  backstory="Oversees the entire operation, ensuring that all agents work cohesively towards the goal, facilitating communication and integration between the different stages of the task.",
  # llm=overseer_model_qwen,
  llm = katonic_llm,
  allow_delegation=True,
)

# Agent optimized for tool use tasks - Office Assistant
tooluser = Agent(
  role='Office Assistant',
  goal='Assist other agents by using system tools as requested. Choices: search_tool, wiki_tool, human_tool ',
  verbose=True,
  backstory="Adept at calling langchain tools. search_tool searches the web, wiki_tool searches a specific wiki topic, human_tool requests human intervention if perplexity seems high.",
  # llm=coding_model,
  llm = katonic_llm,
  allow_delegation=True,
  tools=[search_tool]
)

from crewai import Task
from crewai import Crew, Process, Agent

# Install duckduckgo-search for this example:
# !pip install -U duckduckgo-search



# Define tasks outside of the list
task1 = Task(description="Identify the main objectives of the large task and decompose it into smaller, manageable subtasks.",
            expected_output = "A list of subtasks.",
            agent=coder)

task2 = Task(description="Establish a timeline for each phase of the task, ensuring timely progress.", 
             expected_output = "A timeline for each phase of the task.",
             agent=generalist)

task3 = Task(description="Generate an initial solution for each decomposed subtask.", 
             expected_output = "An initial solution for each subtask.",
             agent=instructor)

task4 = Task(description="Document the solution generation process and outcomes clearly.", 
             expected_output = "A clear Documentation of the solution generation process and outcomes.",
             agent=writer)

task5 = Task(description="Review and iteratively improve the solutions for subtasks.", 
             expected_output = "Improved solutions for subtasks.",
             agent=math_scientist) # Updated to use math_scientist for iterative improvement

task6 = Task(description="Coordinate the integration of solutions and oversee the entire operation.", 
             expected_output = "Integration of solutions and oversee the entire operation.",
             agent=overseer_qwen)

task7 = Task(description="Monitor and adjust strategies for improved efficiency and solution integration.", 
             expected_output = "Improved efficiency and solution integration.",
             agent=generalist)

# Then, include these tasks directly in the list
tasks = [task1, task2, task3, task4, task5, task6, task7]

# Now, when forming the crew, refer directly to this list
crew = Crew(
  agents=[generalist, coder, tooluser, overseer_qwen, instructor, writer, math_scientist],  # Ensure all relevant agents are included
  tasks=tasks,
  process=Process.hierarchical,    #replace with sequential to make the script work
  # manager_llm=overseer_model_qwen 
  manager_llm = katonic_llm
)

# Starting the task execution process
result = crew.kickoff()
print(result)