# DISHA Backend

The intelligence layer for the DISHA Agentic AI Platform.

## Architecture

This is a modular FastAPI application structured for real intelligence:

- **Sources & Ingestion**: Abstracted source fetching with multi-stage deduplication.
- **LLM Extraction**: Uses Gemini to extract structured Pydantic models from raw text, grounded with evidence snippets.
- **Verification Engine**: Multi-stage deduplication, contradiction detection across sources.
- **Explainable Trust**: Computes a Trust Score based on source credibility, field completeness, cross-source agreement, and freshness.
- **Eligibility Engine**: Deterministic rules checking if a student is eligible (separate from relevance).
- **Matching Engine**: Deterministic + semantic matching considering skills, interests, career goals, format, and cost.
- **Roadmap Agent**: Skill gap analysis mapped to actionable learning resources.

## Demo Mode

For the hackathon demo, the application runs entirely in memory without requiring a live Supabase instance or Gemini API key. It uses a robust seed data set containing 15 meticulously crafted opportunities covering all edge cases (missing deadlines, contradictions, duplicates, expirations).

## Setup

```bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn app.main:app --reload
```

## API Documentation

Once running, view the interactive API documentation at:
- [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
