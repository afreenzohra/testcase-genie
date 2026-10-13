# 🎯 TestCase-Genie: Prompt Engineering Strategy & Rationale

Prompts in TestCase-Genie are treated as first-class software components. Rather than burying instructions inside Python string constants, they are isolated in `prompts/` to enable rapid iteration, independent version control, and clear architectural rationale.

---

## 1. System Prompt (`prompts/system_prompt.txt`)

### Persona & Role Anchoring
```text
You are a Staff QA Architect and Principal Test Automation Engineer with decades
of experience designing mission-critical enterprise test suites.
```
* **Why it exists**: LLMs default to shallow "happy path" checks unless an authoritative role is established. Specifying *Staff QA Architect* primes the model to think defensively, prioritizing boundary conditions, fault tolerance, and security implications.

### Coverage Mandates
The prompt strictly enumerates:
1. **Positive Scenarios**: Standard workflows and expected happy paths.
2. **Negative Scenarios**: Invalid data formats, missing headers, unauthenticated states, payload limits.
3. **Boundary Value Analysis (BVA)**: Min/max thresholds, zero-lengths, off-by-one indices.
4. **Edge & Concurrency Conditions**: Session timeouts, concurrent requests, idempotency bugs, double submissions.

* **Why it exists**: Prevents LLMs from producing 5 trivial variations of the same happy path scenario.

---

## 2. Test Case Generation Prompt (`prompts/test_case_generation.txt`)

### Strict Structural Contract
The generation prompt provides an exact JSON schema matching Pydantic's `TestCaseSuite`:
```json
{
  "title": "Feature or Suite Title",
  "description": "Short summary",
  "app_type": "{app_type}",
  "test_cases": [
    {
      "id": "TC-001",
      "title": "Descriptive title",
      "type": "positive",
      "preconditions": ["..."],
      "steps": ["..."],
      "expected_result": "Exact verifiable outcome",
      "priority": "high"
    }
  ]
}
```
* **Why it exists**: Direct schema specification minimizes hallucination and ensures deterministic deserialization into Pydantic models.

### Scenario Distribution Bias
```text
Distribution:
- Positive / Happy Path: ~40%
- Negative / Error Handling: ~35%
- Edge / Boundary / Permission: ~25%
```
* **Why it exists**: Without distribution constraints, models generate ~90% positive cases. This ratio enforces real-world quality assurance rigor.

---

## 3. Automation Code Generation Prompt (`prompts/code_generation.txt`)

### Enforcing Page Object Model (POM)
```text
1. Pattern: Implement the Page Object Model (POM).
   - Create Page Classes isolating web elements and actions.
   - For all web elements, use clearly marked TODO placeholders for locators:
     * Selenium: ELEMENT = (By.ID, "TODO_replace_with_actual_id")  # TODO: Define locator
     * Playwright: self.element = page.locator("TODO_replace_with_selector")  # TODO: Define locator
```
* **Why it exists**: Because the LLM does not have access to the user's private, runtime web DOM, generating fabricated selectors causes immediate runtime failure. Explicit `# TODO` markers make it immediately actionable for engineers to replace placeholders with real selectors.

### 1:1 Requirement-to-Test Traceability
```text
2. Test Class / Test Functions:
   - Provide standard pytest fixtures for browser/driver lifecycle.
   - Create one test method per test case (e.g. test_tc_001_...), referencing Test ID.
```
* **Why it exists**: Guarantees clear mapping between documented manual QA scenarios and automated test methods.
