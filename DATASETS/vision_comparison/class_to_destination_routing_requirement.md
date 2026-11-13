# Class-to-Destination Routing — Architectural Requirement

{
  "doc_type": "architectural_requirement",
  "title": "Class-to-Destination Routing \u2014 Architectural Requirement (NOT an implemented capability)",
  "status": "PENDING IMPLEMENTATION",
  "reason": "King Wen has multi-label classification but no routing mechanism. The gap is between classification and derived dataset generation.",
  "design_principle": "Multi-destination routing with one canonical evidence record",
  "key_rules": [
    "Original source, page identity, crop, coordinates, producer lineage, and adjudication remain authoritative",
    "Multiple classifications with confidence and evidence are preserved",
    "Routing decisions are zero or more destinations derived from classifications",
    "Derived outputs: mathematical recovery dataset, graph and plot dataset, symbol and glyph dataset, figure and diagram dataset, text and table dataset, unresolved review dataset",
    "A record can appear in multiple derived datasets while retaining one original identity and provenance chain",
    "No duplication of underlying evidence or confusion between derived records and independent observations"
  ],
  "current_state": "Classification implemented (math_symbol_classifier.py, build_benchmark_representativeness.py, math_pdf_parser.py)",
  "missing": "General class-to-destination routing layer (separate from adjudicator)",
  "evidence": "routing_coverage_audit.json, adjudication_candidates_v2_disposition.json"
}