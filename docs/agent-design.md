# TruthLens AI - Agent Design Specification

## Multi-Agent Roster

| Agent Name | Function | Input | Output |
| :--- | :--- | :--- | :--- |
| **Claim Analyzer** | Deconstructs claim into entities, topic, time sensitivity, & questions | Factual Claim | Structured JSON Metadata |
| **Planner Agent** | Generates dynamic query strategy tailored to claim | Claim Analysis | Targeted Search Queries |
| **Research Agent** | Executes web searches, scrapes pages, applies injection boundaries | Search Queries | Cleaned Web Sources |
| **Source Credibility** | Evaluates authority, recency, domain reputation & primary nature | Web Sources | Credibility Score (0.0-1.0) |
| **Evidence Extraction** | Extracts factual statements and assigns stance (SUPPORTS/CONTRADICTS) | Claim + Content | Extracted Evidence Items |
| **Contradiction Detection** | Identifies date, definition, or methodological mismatches | Evidence Items | Contradiction Records |
| **Verdict Agent** | Reason over evidence to produce standard verdict | Evidence + Contradictions | Standard Verdict + Reasoning |
| **Verification Agent** | Quality assurance loop for citation accuracy & hallucination check | Proposed Verdict | Verified (True/False) |

## Deterministic Confidence Formula

$$\text{Score} = 0.30 \cdot S_{\text{quality}} + 0.25 \cdot E_{\text{agreement}} + 0.20 \cdot E_{\text{strength}} + 0.10 \cdot R_{\text{recency}} + 0.10 \cdot S_{\text{indep}} - 0.05 \cdot P_{\text{contradiction}}$$

## Human-in-the-Loop Triggers
Human review is required if:
1. Deterministic Confidence Score < 0.60
2. Contradiction Severity > 0.60
3. Low average source credibility (< 0.40)
