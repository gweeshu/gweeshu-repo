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

    def generate_summary(self, text: str, pass_number: int, title: str, image_count: int = 0) -> str:
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
- Aim for 300-500 words
- Help the student understand "what" is covered, not the details""",
            2: """Create a DETAILED SUMMARY suitable for Pass 2 study:
- Include important details, mechanisms, and relationships
- Organize by topic with clear subsections
- Include key terms, definitions, and concepts
- Add important examples and clinical relevance
- Aim for 800-1200 words
- Help the student understand "how" and "why" things work""",
            3: """Create a COMPREHENSIVE, GRANULAR summary suitable for Pass 3 study:
- Include all important details, mechanisms, pathways
- Cover exceptions, special cases, and clinical pearls
- Include specific numbers, values, classifications
- Add mnemonics, memory aids, and study tips
- Be thorough and exam-focused
- Aim for 1500-2500 words
- Help the student master all testable material"""
        }

        image_note = ""
        if image_count > 0:
            image_note = f"\n\nNote: This lecture has {image_count} images extracted from the source materials. Reference relevant diagrams and images when appropriate using placeholders like '[See Image: description]'."

        prompt = f"""You are a medical education expert. Create a summary collating information from multiple source documents for this lecture: "{title}"

{pass_instructions.get(pass_number, pass_instructions[1])}{image_note}

Content from all source documents:
{text[:50000]}

Format your response in clean, well-structured markdown:
- Use ## for main sections
- Use ### for subsections
- Use **bold** for key terms and important concepts
- Use bullet points and numbered lists for clarity
- Use tables when comparing information
- Add horizontal rules (---) to separate major sections

Make the summary comprehensive by integrating information from all source documents."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=8000,
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
