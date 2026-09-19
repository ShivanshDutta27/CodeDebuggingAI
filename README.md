# 🔧 Fixie: Polyglot AI Agent Debugger Studio

An intelligent multi-language debugging studio powered by coordinated LangGraph AI agents and the Google Gemini API. Fixie automatically profiles your code environment (LeetCode algorithms vs. MERN web applications vs. compiled CLI apps), checks syntax/compiler rules across any programming language (C++, Python, JavaScript/React, Java, Go, Rust), deduces intent, synthesizes idiomatic fixes, and produces verified test cases or browser runbooks.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![React](https://img.shields.io/badge/React-18-blue.svg)
![LangChain](https://img.shields.io/badge/LangChain-🦜🔗-green.svg)
![Gemini](https://img.shields.io/badge/Google-Gemini_API-blue.svg)

## ✨ Features

- 🌐 **Context & Environment Profiler**: Auto-detects programming languages (C++, Python, JS/TS, Java, Go, Rust) and project types (`leetcode`, `mern`, `compiled_app`, `backend_api`).
- 🤖 **5-Agent LangGraph Pipeline**: Real-time coordinated workflow:
  1. **Context Profiler**: Detects language, project type, and build commands.
  2. **Compiler & Syntax Auditor**: Language-specific AST and memory safety analysis.
  3. **Logic Reasoner**: Intent, algorithmic data flow, and complexity analysis.
  4. **Fix Architect**: Idiomatic, complete code repairs.
  5. **Verification Harness**: Generates LeetCode test cases + test runner, or MERN browser verification runbooks.
- ⚡ **Zero-Simulation Real-Time SSE**: Frontend updates strictly as Gemini streams genuine execution chunks.
- 🎨 **Minimalist Studio UI**: Built with React + Vite and custom Vanilla CSS with dark obsidian aesthetics, code editor with gutter numbers, confidence scores, and MySQL history storage.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ (3.10+ preferred)
- Google Gemini API Key
- MySQL 8.0+ (optional, for session persistence)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/kawish918/Fixie-AI-Agent-Debugger.git
   cd fixie-ai-debugger
   ```

2. **Create virtual environment**
   ```bash
   python -m venv fixie
   fixie\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   
   Copy `.env.example` to `.env` and fill in your Gemini API key:
   ```bash
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-1.5-flash
   ```

### Usage

1. **Run on the example buggy code**
   ```bash
   python main.py
   ```

2. **Add your own buggy Python files**
   ```bash
   # Place your .py file in the examples/ directory
   # Update main.py to point to your file:
   code = read_python_file('examples/your_buggy_file.py')
   ```

## 📁 Project Structure

```
fixie-ai-debugger/
├── agents/
│   ├── fix_suggester.py      # AI agent for generating fixes
│   ├── logic_reasoner.py     # AI agent for understanding code logic
│   └── syntax_checker.py     # AI agent for detecting syntax errors
├── core/
│   ├── agent_runner.py       # Simple agent orchestration
│   ├── input_handler.py      # File reading utilities
│   ├── langgraph_runner.py   # LangGraph workflow management
│   └── llama_interface.py    # Ollama API interface
├── examples/
│   └── buggy_code.py         # Sample buggy code for testing
├── main.py                   # Main application entry point
└── README.md
```

## 🔄 How It Works

Fixie uses a coordinated multi-agent workflow:

1. **Syntax Checker Agent** 🔍
   - Analyzes code for syntax and runtime errors
   - Identifies problematic lines and severity levels

2. **Logic Reasoner Agent** 🧠
   - Understands the intended purpose of the code
   - Provides context for fix generation

3. **Fix Suggester Agent** 🛠️
   - Combines bug report and logic analysis
   - Generates complete, executable fix suggestions
   - Provides confidence scores

4. **LangGraph Orchestration** 🔄
   - Manages agent workflow and data flow
   - Ensures proper sequencing and state management

## 📊 Example Output

```
--- Fixie AI Debugger ---

Original Code:
def add_nums(a, b):
    return a + b + c

🔍 Debug Results:
==================================================
🐛 Bug Found: NameError - variable 'c' is not defined
📍 Line Number: 2
⚠️  Severity: HIGH
--------------------------------------------------
📊 Fix Confidence: 0.95
💡 Explanation: Variable 'c' is undefined in the function
🔧 Suggested Fix:
def add_nums(a, b):
    return a + b
```

## ⚙️ Configuration

### Using Different Models

Update the model in any agent:

```python
# In agents/fix_suggester.py
class FixSuggester:
    def __init__(self, model="llama3.2"):  # Change model here
        self.model = model
```

### Customizing Prompts

Modify prompts in each agent class to suit your debugging needs:

```python
# In agents/syntax_checker.py
def check(self, code: str) -> dict:
    prompt = f"""Your custom prompt here..."""
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📋 Future Enhancements

- [ ] Support for multiple programming languages
- [ ] Integration with popular IDEs
- [ ] Web interface for easier usage
- [ ] Code execution validation
- [ ] Integration with static analysis tools
- [ ] Custom rule definitions
- [ ] Batch processing of multiple files

## 🔧 Troubleshooting

### Common Issues

**Ollama not found:**
```bash
# Make sure Ollama is installed and in PATH
ollama --version
```

**Model not available:**
```bash
# Pull the required model
ollama pull llama3.2
```

**LangChain import errors:**
```bash
# Install missing dependencies
pip install langchain langgraph
```

**Permission errors on Windows:**
```bash
# Run as administrator or check antivirus settings
```

## 📚 Resources

- [LangChain Documentation](https://docs.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Ollama Documentation](https://ollama.ai/docs)
- [Llama 3.2 Model Card](https://ollama.ai/library/llama3.2)
- [Get LangSmith API Key](https://docs.smith.langchain.com/administration/how_to_guides/organization_management/create_account_api_key)
- [LangGraph Local Server](https://langchain-ai.github.io/langgraph/tutorials/langgraph-platform/local-server/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

##  Acknowledgments

- [LangChain](https://langchain.com/) for the agent framework
- [Ollama](https://ollama.ai/) for local AI model hosting
- [Meta](https://ai.meta.com/) for the Llama 3.2 model

---

*Star ⭐ this repo if you find it helpful!*
