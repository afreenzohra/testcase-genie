# 🧞 TestCase-Genie: Architecture & System Design

TestCase-Genie is an intelligent test engineering agent designed to bridge the gap between product requirements (User Stories) and automated test execution. It synthesizes structured, ISTQB-aligned test scenarios (positive, negative, edge, and boundary cases) and generates starter automation code adhering to the **Page Object Model (POM)** in Python with **Playwright** or **Selenium**.

---

## 1. High-Level System Architecture

```mermaid
flowchart TD
    subgraph Inputs ["Input Layer"]
        StoryText["User Story Text"]
        StoryFile["Story File (.txt / .md)"]
        Config["Config (Framework, Count, Domain)"]
    end

    subgraph Interfaces ["User Interfaces"]
        CLI["Typer CLI (cli.py)"]
        WebUI["Streamlit UI (app.py)"]
    end

    subgraph CoreEngine ["TestCase-Genie Core Engine"]
        Generator["TestCaseGenerator (generator.py)"]
        Agent["GeminiAgent (agent.py)"]
        Prompts["Prompt Templates (prompts/)"]
        Models["Pydantic Schemas (models.py)"]
    end

    subgraph LLM ["Google Gemini AI"]
        GeminiAPI["Google Gemini 2.5 Flash / Pro (google-genai SDK)"]
    end

    subgraph Serialization ["Export & Output Layer"]
        Exporter["Exporter Engine (exporter.py)"]
        JSONOut["test_suite.json"]
        MDOut["test_suite.md"]
        CSVOut["test_suite.csv"]
        CodeOut["test_automation.py (POM)"]
    end

    Inputs --> CLI
    Inputs --> WebUI
    CLI --> Generator
    WebUI --> Generator
    Generator --> Prompts
    Generator --> Agent
    Agent --> GeminiAPI
    GeminiAPI --> Agent
    Agent --> Generator
    Generator --> Models
    Models --> Exporter
    Exporter --> JSONOut
    Exporter --> MDOut
    Exporter --> CSVOut
    Exporter --> CodeOut
```

---

## 2. Two-Stage Generation Pipeline

The generation pipeline decouples logical test design from syntax-specific automation code generation:

```mermaid
sequenceDiagram
    autonumber
    actor User as QA Engineer / Developer
    participant UI as CLI / Streamlit
    participant Gen as TestCaseGenerator
    participant Agent as GeminiAgent
    participant LLM as Google Gemini API
    participant Model as Pydantic Models

    User->>UI: Submit User Story + Framework (Playwright/Selenium)
    UI->>Gen: generate(user_story, config)
    
    rect rgb(240, 248, 255)
        Note over Gen,LLM: Stage 1: Structured Test Case Synthesis
        Gen->>Agent: generate_content(test_gen_prompt, system_prompt)
        Agent->>LLM: models.generate_content(...)
        LLM-->>Agent: JSON Response with Scenarios
        Agent-->>Gen: Raw Text
        Gen->>Model: TestCaseSuite.model_validate(json_payload)
        alt JSON Parse or Validation Failure
            Gen->>Agent: Retry with Repair Prompt (Error Diagnostics)
            Agent->>LLM: Regenerate with strict JSON schema
            LLM-->>Agent: Repaired JSON
            Gen->>Model: Re-validate schema
        end
    end

    rect rgb(255, 250, 240)
        Note over Gen,LLM: Stage 2: Page Object Model Code Generation
        Gen->>Agent: generate_content(code_gen_prompt, system_prompt)
        Agent->>LLM: models.generate_content(...)
        LLM-->>Agent: Python Code with POM & Locators
        Agent-->>Gen: Code Text
        Gen->>Gen: clean_python_code(strip markdown fences)
    end

    Gen-->>UI: Complete TestCaseSuite (Cases + Code)
    UI->>User: Display UI Tables, Syntax-Highlighted Code & Downloads
```

---

## 3. Resilience and Defensive Design

1. **Deterministic Pydantic Validation**:
   - `TestCase` sanitizes flexible model responses (e.g., coercing multiline string steps into lists of strings, case-insensitively normalizing test types and priority levels).
2. **Autonomous Error Repair**:
   - If the LLM generates slightly malformed JSON or omits a required field, the generator detects the failure and immediately issues a targeted repair prompt providing the exact validation diagnostic.
3. **Rate-Limit & Transient Error Backoff**:
   - Built-in exponential backoff gracefully handles API quotas (HTTP 429) or transient network hiccups without crashing client workflows.
4. **Environment Isolation**:
   - Strict separation of credentials via `.env` and `.gitignore`. No credentials or API tokens are ever logged, printed, or exported.

---

## 4. Automation Code Design: Page Object Model (POM)

Generated code strictly avoids monolithic scripts with fragile inline selectors:
- **Page Classes (`LoginPage`, `CheckoutPage`, `TransferPage`)**: Encapsulate locators and user interactions.
- **`# TODO: Define locator for <element>` Placeholders**: Instantly signal where QA engineers need to plug in their specific production DOM selectors.
- **Standard `pytest` Fixtures**: Setup and teardown browser instances cleanly for CI/CD pipelines.
- **Traceability**: Each generated test function directly corresponds to a test case ID (e.g. `test_tc_001_...`).
