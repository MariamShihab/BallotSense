# BallotSense MVP - AGENTS.md

## 1. Project Intent (The "Why")
BallotSense is a serverless voter education platform localized for the Santa Clara County Primary Election. The application utilizes a strict Retrieval-Augmented Generation (RAG) pipeline to analyze mail-in ballots against official voter guide data. The primary architectural directive is traceability: every AI-generated claim must be cited back to a verified Firestore document.

## 2. Tech Stack (The "What")
- **Frontend:** Remix (React), Tailwind CSS
- **Backend:** Python (FastAPI)
- **Infrastructure:** Google Cloud Platform (Cloud Run for Serverless execution)
- **Database:** Google Cloud Firestore (Native Vector Search for embeddings)
- **AI Engine:** Google Gemini API (Multimodal OCR & Text Generation)

## 3. Operational Directives (The "How")
- **State Management:** All Cloud Run functions must be entirely stateless. Do not write data to local disk; handle all image processing and embeddings in-memory.
- **Python Conventions:** Utilize Python's dynamic typing and dictionary structures in place of manual memory allocation or rigid structs. Use `pydantic` for strict schema validation on all incoming API requests to prevent malformed data.
- **Vector Search:** When querying Firestore, strictly use its native Cosine Similarity distance measure. Do not attempt to integrate third-party vector databases.
- **RAG Enforcement:** When interacting with the Gemini API, the system prompt must explicitly forbid the model from using its baseline training data. It must only synthesize answers from the retrieved Firestore chunks.
- **UI Styling:** All component styling must be handled via Tailwind utility classes. Do not create separate CSS files unless absolutely necessary for complex overrides.

## 4. Boundaries (Do Not Modify)
- **.env Files:** Never commit environment variables containing GCP Service Account JSON keys or Gemini API keys.
- **Database Rules:** Do not alter the Firestore security rules without explicit human approval. Destructive operations require human sign-off.
- **Agent Context:** Do not modify this AGENTS.md file autonomously. All changes to these core rules must go through human code review.
