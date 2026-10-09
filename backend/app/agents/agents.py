import json
import logging
from typing import Dict, Any, List, Optional
from app.core.llm_provider import get_llm_provider
from app.tools.tools import web_search, fetch_webpage, parse_webpage, extract_metadata

logger = logging.getLogger(__name__)

class ClaimAnalyzerAgent:
    """Agent A: Deconstructs user claim into structured metadata & research questions."""
    
    async def analyze(self, claim: str) -> Dict[str, Any]:
        system_prompt = (
            "You are an expert Claim Analyzer AI in fact-checking and journalism. "
            "Analyze the given factual claim and deconstruct it into structured fields."
        )
        prompt = (
            f"Analyze the following claim:\n\"{claim}\"\n\n"
            "Return JSON matching this exact structure:\n"
            "{\n"
            "  \"claim\": \"<original claim>\",\n"
            "  \"topic\": \"<primary topic area>\",\n"
            "  \"entities\": [\"<entity 1>\", \"<entity 2>\"],\n"
            "  \"claim_type\": \"<Scientific / Health / Political / Historical / Technology / Social>\",\n"
            "  \"time_sensitive\": true/false,\n"
            "  \"investigation_questions\": [\n"
            "    \"<key investigation question 1>\",\n"
            "    \"<key investigation question 2>\"\n"
            "  ]\n"
            "}"
        )
        llm = get_llm_provider()
        return await llm.generate_json(prompt, system_prompt)

class PlannerAgent:
    """Agent B: Generates dynamic, claim-specific search queries and strategy."""

    async def plan(self, claim_analysis: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = (
            "You are a Senior Fact-Checking Investigation Planner. "
            "Design a targeted search strategy to gather empirical evidence."
        )
        prompt = (
            f"Given the claim analysis:\n{json.dumps(claim_analysis, indent=2)}\n\n"
            "Generate 3-4 targeted, diverse search queries to find scientific reports, official statements, and empirical studies.\n"
            "Return JSON:\n"
            "{\n"
            "  \"queries\": [\"query 1\", \"query 2\", \"query 3\"],\n"
            "  \"rationale\": \"<brief search rationale>\"\n"
            "}"
        )
        llm = get_llm_provider()
        return await llm.generate_json(prompt, system_prompt)

class ResearchAgent:
    """Agent C: Executes web searches, fetches webpages, extracts text safely."""

    async def execute_research(self, search_queries: List[str], max_sources_per_query: int = 2) -> List[Dict[str, Any]]:
        sources = []
        seen_urls = set()

        for q in search_queries:
            if len(sources) >= 3:
                break
            results = await web_search(q, max_results=max_sources_per_query)
            for item in results:
                if len(sources) >= 3:
                    break
                url = item.get("url")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)

                # Fetch and parse webpage content
                page_data = await fetch_webpage(url)
                parsed = parse_webpage(page_data.get("html", ""), url=url, title=item.get("title", ""), snippet=item.get("snippet", "")) if page_data.get("accessible") else {}
                meta = extract_metadata(url, page_data.get("html", "")) if page_data.get("accessible") else {}

                sources.append({
                    "url": url,
                    "title": item.get("title") or parsed.get("title") or "Web Source",
                    "domain": item.get("domain") or meta.get("domain") or (url.split("/")[2] if "//" in url else url),
                    "publication_date": item.get("publication_date") or meta.get("pub_date") or "Unknown",
                    "snippet": item.get("snippet", ""),
                    "source_type": item.get("source_type", "web"),
                    "content": parsed.get("clean_text", item.get("snippet", "")),
                    "is_accessible": page_data.get("accessible", True)
                })
        return sources


class SourceCredibilityAgent:
    """Agent D: Evaluates credibility scores for retrieved sources."""

    async def evaluate_source(self, source: Dict[str, Any], claim: str) -> Dict[str, Any]:
        system_prompt = (
            "You are a Media & Academic Credibility Evaluation AI. "
            "Score the reliability of the source objectively."
        )
        prompt = (
            f"Claim: \"{claim}\"\n\n"
            f"Source Domain: {source.get('domain')}\n"
            f"Source Title: {source.get('title')}\n"
            f"Source Type: {source.get('source_type')}\n"
            f"Publication Date: {source.get('publication_date')}\n"
            f"Content Snippet: {source.get('snippet')}\n\n"
            "Evaluate this source across 6 metrics (0.0 to 1.0):\n"
            "1. authority_score (peer-reviewed / medical / official vs blog)\n"
            "2. recency_score (timeliness relative to claim)\n"
            "3. primary_secondary_score (primary empirical study vs aggregated report)\n"
            "4. evidence_quality_score (methodological transparency)\n"
            "5. domain_reputation_score (institutional standing)\n"
            "6. citation_quality_score (reference completeness)\n\n"
            "Return JSON:\n"
            "{\n"
            "  \"authority_score\": 0.85,\n"
            "  \"recency_score\": 0.90,\n"
            "  \"primary_secondary_score\": 0.80,\n"
            "  \"evidence_quality_score\": 0.85,\n"
            "  \"domain_reputation_score\": 0.85,\n"
            "  \"citation_quality_score\": 0.80,\n"
            "  \"explanation\": \"<short justification>\"\n"
            "}"
        )
        llm = get_llm_provider()
        res = await llm.generate_json(prompt, system_prompt)
        
        # Calculate final weighted credibility score
        scores = [
            res.get("authority_score", 0.5),
            res.get("recency_score", 0.5),
            res.get("primary_secondary_score", 0.5),
            res.get("evidence_quality_score", 0.5),
            res.get("domain_reputation_score", 0.5),
            res.get("citation_quality_score", 0.5)
        ]
        res["final_credibility_score"] = round(sum(scores) / len(scores), 4)
        return res

class EvidenceExtractionAgent:
    """Agent E: Extracts precise evidence statements and stance relative to claim."""

    async def extract_evidence(self, claim: str, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        system_prompt = (
            "You are an Evidence Extraction Specialist AI. "
            "Extract ONLY factual evidence directly related to the user claim. Never fabricate evidence."
        )
        prompt = (
            f"Claim to verify: \"{claim}\"\n\n"
            f"Source Title: {source.get('title')}\n"
            f"Source URL: {source.get('url')}\n"
            f"Source Content:\n{source.get('content')[:2000]}\n\n"
            "Extract evidence items from this source. Return JSON:\n"
            "{\n"
            "  \"evidence\": [\n"
            "    {\n"
            "      \"evidence_text\": \"<exact statement/data from content>\",\n"
            "      \"stance\": \"<SUPPORTS / CONTRADICTS / NEUTRAL>\",\n"
            "      \"strength\": 0.85,\n"
            "      \"context\": \"<contextual note>\"\n"
            "    }\n"
            "  ]\n"
            "}"
        )
        llm = get_llm_provider()
        res = await llm.generate_json(prompt, system_prompt)
        return res.get("evidence", [])

class ContradictionDetectionAgent:
    """Agent F: Detects disagreement, date mismatch, or methodological conflicts between sources."""

    async def detect_contradictions(self, claim: str, evidence_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if len(evidence_items) < 2:
            return []

        system_prompt = (
            "You are a Logical Contradiction & Discrepancy Analysis Agent. "
            "Analyze collected evidence items for conflicting statements, date discrepancies, or methodological differences."
        )
        prompt = (
            f"Claim: \"{claim}\"\n\n"
            f"Collected Evidence Items:\n{json.dumps(evidence_items, indent=2)}\n\n"
            "Identify contradictions between sources. Return JSON:\n"
            "{\n"
            "  \"contradictions\": [\n"
            "    {\n"
            "      \"supporting_evidence_ids\": [],\n"
            "      \"contradicting_evidence_ids\": [],\n"
            "      \"contradiction_type\": \"<direct_factual / methodological / date_difference / definition_difference / population_difference>\",\n"
            "      \"description\": \"<explanation of conflict>\",\n"
            "      \"severity\": 0.70\n"
            "    }\n"
            "  ]\n"
            "}"
        )
        llm = get_llm_provider()
        res = await llm.generate_json(prompt, system_prompt)
        return res.get("contradictions", [])

class VerdictAgent:
    """Agent G: Synthesizes evidence to produce final nuanced verdict."""

    async def generate_verdict(
        self,
        claim: str,
        evidence_items: List[Dict[str, Any]],
        contradictions: List[Dict[str, Any]],
        confidence_score: float
    ) -> Dict[str, Any]:
        system_prompt = (
            "You are a Master Fact Verification Ombudsman. "
            "Reason over structured evidence and determine a fair, nuanced verdict.\n"
            "Allowed verdicts: TRUE, MOSTLY TRUE, PARTIALLY TRUE, MISLEADING, MOSTLY FALSE, FALSE, UNVERIFIED, INSUFFICIENT EVIDENCE."
        )
        prompt = (
            f"Claim: \"{claim}\"\n"
            f"Calculated Deterministic Confidence Score: {confidence_score:.4f}\n\n"
            f"Evidence Items:\n{json.dumps(evidence_items, indent=2)}\n\n"
            f"Detected Contradictions:\n{json.dumps(contradictions, indent=2)}\n\n"
            "Synthesize final verdict. Return JSON:\n"
            "{\n"
            "  \"verdict\": \"<ONE OF ALLOWED VERDICTS>\",\n"
            "  \"reasoning_summary\": \"<comprehensive multi-sentence synthesis>\",\n"
            "  \"key_evidence\": [\"<key point 1>\", \"<key point 2>\"],\n"
            "  \"limitations\": [\"<limitation 1>\", \"<limitation 2>\"]\n"
            "}"
        )
        llm = get_llm_provider()
        return await llm.generate_json(prompt, system_prompt)

class VerificationAgent:
    """Agent H: Reviews verdict for hallucination, unbacked claims, or logical inconsistencies. Max retries: 3."""

    async def verify_verdict(
        self,
        claim: str,
        verdict_data: Dict[str, Any],
        evidence_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        system_prompt = (
            "You are an Independent Quality Assurance & Verification Agent. "
            "Rigorously evaluate the proposed verdict against the raw evidence."
        )
        prompt = (
            f"Claim: \"{claim}\"\n\n"
            f"Proposed Verdict: {json.dumps(verdict_data, indent=2)}\n\n"
            f"Raw Evidence Items:\n{json.dumps(evidence_items, indent=2)}\n\n"
            "Verify the verdict:\n"
            "1. Is every major claim supported by raw evidence?\n"
            "2. Are citations valid?\n"
            "3. Is any information hallucinated?\n"
            "4. Is the verdict consistent with evidence?\n\n"
            "Return JSON:\n"
            "{\n"
            "  \"verified\": true/false,\n"
            "  \"all_claims_supported\": true/false,\n"
            "  \"citations_valid\": true/false,\n"
            "  \"hallucinations_detected\": true/false,\n"
            "  \"verdict_consistent\": true/false,\n"
            "  \"confidence_justified\": true/false,\n"
            "  \"notes\": \"<verification feedback / revision notes if unverified>\"\n"
            "}"
        )
        llm = get_llm_provider()
        return await llm.generate_json(prompt, system_prompt)
