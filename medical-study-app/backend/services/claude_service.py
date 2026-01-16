from anthropic import Anthropic
import os
import json

class ClaudeService:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-opus-4-5-20251101"

    def classify_document(self, text: str, filename: str) -> dict:
        """
        Classify a document into a subject and extract a lecture title.
        Returns: {"subject": "Anatomy", "title": "Brainstem Structure"}
        """
        prompt = f"""You are analyzing a medical school lecture document. Based on the content and filename, determine:
1. The subject/class (e.g., Anatomy, Physiology, Pharmacology, Pathology, etc.)
2. A clear, concise lecture title

Filename: {filename}

Document content (first 3000 characters):
{text[:3000]}

Respond with ONLY a JSON object in this format:
{{"subject": "Subject Name", "title": "Lecture Title"}}

Be specific with the subject name. Common medical school subjects include:
- Anatomy
- Physiology
- Biochemistry
- Pharmacology
- Pathology
- Microbiology
- Immunology
- Neuroscience
- Histology
- Embryology
- Clinical Skills
- etc.
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )

        result_text = response.content[0].text.strip()

        # Try to parse JSON
        try:
            # Remove markdown code blocks if present
            if result_text.startswith("```"):
                result_text = result_text.split("```")[1]
                if result_text.startswith("json"):
                    result_text = result_text[4:]
                result_text = result_text.strip()

            return json.loads(result_text)
        except json.JSONDecodeError:
            # Fallback parsing
            return {"subject": "Uncategorized", "title": filename}

    def generate_summary(self, text: str, pass_number: int, title: str) -> str:
        """
        Generate a summary for a specific pass level.
        Pass 1: Broad overview (key concepts only)
        Pass 2: Detailed summary (important details)
        Pass 3: Granular/comprehensive (all details)
        """
        pass_instructions = {
            1: """Create a BROAD OVERVIEW suitable for Pass 1 study:
- Focus only on the main topics and key concepts
- Use bullet points and clear headers
- Keep it high-level (like a table of contents with brief descriptions)
- Aim for 200-400 words
- Help the student understand "what" is covered, not the details""",
            2: """Create a DETAILED SUMMARY suitable for Pass 2 study:
- Include important details, mechanisms, and relationships
- Organize by topic with clear subsections
- Include key terms, definitions, and concepts
- Add important examples and clinical relevance
- Aim for 500-1000 words
- Help the student understand "how" and "why" things work""",
            3: """Create a COMPREHENSIVE, GRANULAR summary suitable for Pass 3 study:
- Include all important details, mechanisms, pathways
- Cover exceptions, special cases, and clinical pearls
- Include specific numbers, values, classifications
- Add mnemonics, memory aids, and study tips
- Be thorough and exam-focused
- Aim for 1000-2000 words
- Help the student master all testable material"""
        }

        prompt = f"""You are a medical education expert. Create a summary of this lecture: "{title}"

{pass_instructions.get(pass_number, pass_instructions[1])}

Document content:
{text[:15000]}  # Using first 15k chars to stay within limits

Format your response in clean markdown with headers, bullet points, and emphasis where appropriate."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text.strip()

    def batch_classify_documents(self, documents: list) -> list:
        """
        Classify multiple documents in a single request for efficiency.
        documents: list of {"filename": str, "text": str}
        """
        if not documents:
            return []

        # For now, classify individually. Could optimize later with batch API
        results = []
        for doc in documents:
            try:
                classification = self.classify_document(doc["text"], doc["filename"])
                results.append({
                    "filename": doc["filename"],
                    "subject": classification["subject"],
                    "title": classification["title"]
                })
            except Exception as e:
                results.append({
                    "filename": doc["filename"],
                    "subject": "Uncategorized",
                    "title": doc["filename"],
                    "error": str(e)
                })
        return results
