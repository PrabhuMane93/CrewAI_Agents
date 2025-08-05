# LLM Agent Use Cases: Email Drafting & Tool-Augmented Reasoning

## Overview

This project explores multiple use cases of Large Language Models (LLMs), showcasing:
- 📬 Intelligent email drafting via agent coordination
- 🛠 Tool-augmented reasoning through OpenAI-based workflows

It combines agent-based logic, OpenAI models, and custom tools to simulate real-world LLM-powered interactions.

---

## Project Structure

```
project/
│
├── Email_draft_Usecase/
│   ├── main.py             # Main execution script for email drafting
│   ├── agents.py           # LLM-based agent logic
│   └── graph.py            # Task/agent graph orchestration
│
├── OpenAI_models/
│   ├── Use case 1.py       # Tool-enhanced reasoning with OpenAI
│   ├── Use case 2 - tool .py  # Additional OpenAI-based tool use
│   └── testingFile.txt     # Sample input text for testing
│
├── apitest.py              # Lightweight API or function test script
├── requirements.txt        # All dependencies listed here
└── README.md               # You are here
```

---

## Use Case 1: Email Drafting via Agent Graph

- Constructs a graph of agents with specific roles (e.g., context analyzer, content writer).
- Uses LLM calls under the hood (e.g., OpenAI/GPT) to generate structured email content.
- `main.py` is the entry point.

### Key Files:
- `agents.py`: Defines specialized agent logic.
- `graph.py`: Coordinates agent execution order.
- `main.py`: Loads graph, prompts input, and generates email.

---

## Use Case 2: OpenAI Tool Use

- Uses GPT-style models for tool-augmented tasks (e.g., file summarization, QA).
- `Use case 1.py` and `Use case 2 - tool .py` demonstrate interactive reasoning with API calls or system tools.

---

## Setup Instructions

1. **Clone the repo**
   ```bash
   git clone https://github.com/yourusername/llm-agent-usecases.git
   cd llm-agent-usecases
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Add OpenAI credentials**  
   Set your OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```

---

## Running the Project

### 📬 Email Drafting Agent
```bash
cd Email_draft_Usecase
python main.py
```

### 🛠 Tool Use with OpenAI
```bash
cd OpenAI_models
python "Use case 1.py"
```

---

## Dependencies

- `openai`
- `langchain` (if used)
- `dotenv`
- `pydantic`
- `networkx` (for graph agent logic)
*(See `requirements.txt` for full list)*

---

## License

MIT License


