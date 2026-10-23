"""Module 5: Header-Aware Semantic Document Chunker for Hotel Knowledge

Splits markdown knowledge documents by semantic headers and converts structured
entities (rooms, dining, spa, policies) into dense, retrieval-optimized text chunks.
"""

import re
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class KnowledgeChunk:
    chunk_id: str
    text: str
    metadata: Dict[str, Any]

    @property
    def content(self) -> str:
        return self.text

    @property
    def header(self) -> str:
        return self.metadata.get("section_title", self.metadata.get("doc_title", ""))


class HotelKnowledgeChunker:
    """Chunks both markdown knowledge documents and structured entities."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_markdown_file(self, file_path) -> List[KnowledgeChunk]:
        """Parses a markdown document splitting on H1/H2 section headers."""
        file_path = Path(file_path)
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        file_name = file_path.name
        lines = content.split("\n")

        doc_title = file_name.replace(".md", "").replace("_", " ").title()
        sections: List[Dict[str, str]] = []
        current_header = doc_title
        current_lines: List[str] = []

        for line in lines:
            if line.startswith("# "):
                doc_title = line.replace("# ", "").strip()
            elif line.startswith("## "):
                if current_lines:
                    sections.append({
                        "header": current_header,
                        "text": "\n".join(current_lines).strip()
                    })
                    current_lines = []
                current_header = line.replace("## ", "").strip()
            else:
                current_lines.append(line)

        if current_lines:
            sections.append({
                "header": current_header,
                "text": "\n".join(current_lines).strip()
            })

        chunks: List[KnowledgeChunk] = []
        for idx, sec in enumerate(sections):
            text_body = sec["text"]
            if not text_body:
                continue

            full_chunk_text = f"Document: {doc_title}\nSection: {sec['header']}\n\n{text_body}"
            category = self._infer_category(file_name)

            chunk = KnowledgeChunk(
                chunk_id=f"{file_path.stem}_{idx}",
                text=full_chunk_text,
                metadata={
                    "source_file": file_name,
                    "doc_title": doc_title,
                    "section_title": sec["header"],
                    "category": category
                }
            )
            chunks.append(chunk)

        return chunks

    chunk_file = chunk_markdown_file

    def _infer_category(self, file_name: str) -> str:
        fn = file_name.lower()
        if "room" in fn:
            return "Rooms"
        elif "dining" in fn:
            return "Dining"
        elif "spa" in fn:
            return "Spa"
        elif "amenities" in fn or "facilities" in fn:
            return "Amenities"
        elif "polic" in fn:
            return "Policies"
        elif "attraction" in fn or "transport" in fn:
            return "Local & Transport"
        return "General"


# Alias for compatibility with external references
MarkdownChunker = HotelKnowledgeChunker
