# IndicLive — Data & Glossaries

This directory contains configuration datasets, domain glossaries, and evaluation sentences used by IndicLive's RAG and testing pipelines.

---

## Directory Structure

```
data/
├── README.md
├── glossary/
│   └── sample_glossary.json       # Predefined domain terminology and named-entity mappings
└── test_sentences/
    └── sample_sentences.json      # Benchmark evaluation sentences across Indic languages
```

---

## 1. Domain Glossaries (`data/glossary/`)
Glossary items allow domain operators to define:
- **`preserve`**: Strict preservation of named entities, brands, numbers, or technical acronyms (e.g., "ISRO", "IndicLive", "RailBlock AI") without transliteration or inaccurate translation.
- **`preferred`**: Canonical domain translations for specialized terms (e.g., "Machine Learning" → "இயந்திர கற்றல்" in Tamil).

## 2. Evaluation Sentences (`data/test_sentences/`)
Standardized test corpora for measuring latency, transcript stability, and parallel translation performance across languages.
