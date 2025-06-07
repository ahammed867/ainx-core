# AINX Core

**AINX** is a protocol for agent-to-agent communication designed to be fast, structured, and interoperable — aiming to become the "HTTP for agents."

---

## ✅ What’s implemented (v0.1)

- 🔁 **AINXMessage Protocol**: Structured message format (e.g., `sender::recipient::role::intent::content`)
- 🧠 **Router Agent**: Routes messages to agents based on role
- 👨‍🔬 **Built-in Agents**:
  - `ResearcherAgent`
  - `PlannerAgent`
  - `CriticAgent`
- 💻 **Command Line Interface**: Send agent messages via terminal

---

## 🚀 Usage

Run the CLI with:

```bash
python ainx_cli.py --sender human --intent search --message "What is AINX?"


## 📄 License

MIT
