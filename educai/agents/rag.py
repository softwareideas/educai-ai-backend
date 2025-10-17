import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple, Optional
import logging
import pickle
import json
from educai.config import KNOWLEDGE_BASE_PATH, EMBEDDING_MODEL_NAME, FAISS_INDEX_FILE, CHUNKS_FILE

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MedicalRAG:
    def __init__(self, knowledge_base_path: str = KNOWLEDGE_BASE_PATH, model_name: str = EMBEDDING_MODEL_NAME, index_file: str = FAISS_INDEX_FILE, chunks_file: str = CHUNKS_FILE):
        """
        Retrieval-Augmented Generation system for medical knowledge

        Args:
            knowledge_base_path: Path to directory containing knowledge files
            model_name: Sentence transformer model for embeddings
        """
        self.knowledge_base_path = knowledge_base_path
        self.model_name = model_name
        self.embedding_model = None
        self.index = None
        self.chunks = []
        self.chunk_metadata = []
        self.index_file = index_file
        self.chunks_file = chunks_file

        # Initialize the embedding model
        self._initialize_embedding_model()

        # Load or create the knowledge base
        if self._knowledge_base_exists():
            self._load_knowledge_base()
        else:
            self._create_knowledge_base()

    def _initialize_embedding_model(self):
        """Initialize the sentence transformer model"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.embedding_model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading embedding model: {str(e)}")
            raise

    def _create_knowledge_base(self):
        """Create knowledge base from text files (auto-detected)."""
        logger.info("Creating knowledge base...")

        all_chunks = []
        all_metadata = []

        # Walk knowledge base path recursively and gather all .txt files
        txt_files = []
        for root, _, files in os.walk(self.knowledge_base_path):
            for fn in files:
                if fn.lower().endswith('.txt'):
                    full = os.path.join(root, fn)
                    rel = os.path.relpath(full, self.knowledge_base_path)
                    txt_files.append((full, rel))

        if not txt_files:
            logger.warning("No .txt knowledge files found. Consider adding topic files under the knowledge base path.")

        for full_path, rel_path in txt_files:
            try:
                logger.info(f"Processing {rel_path}...")
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                logger.error(f"Failed to read {rel_path}: {e}")
                continue

            # Split into chunks (paragraphs or sections)
            chunks = self._split_into_chunks(content, rel_path)
            all_chunks.extend(chunks)

            topic = self._extract_topic(rel_path)
            # Create metadata for each chunk
            for i, chunk in enumerate(chunks):
                metadata = {
                    "source": rel_path,
                    "chunk_id": i,
                    "topic": topic,
                    "content_preview": chunk[:100] + "..." if len(chunk) > 100 else chunk
                }
                all_metadata.append(metadata)

        self.chunks = all_chunks
        self.chunk_metadata = all_metadata

        # Create embeddings
        logger.info(f"Creating embeddings for {len(self.chunks)} chunks...")
        embeddings = self.embedding_model.encode(self.chunks, show_progress_bar=True)

        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        faiss.normalize_L2(embeddings)  # Normalize for cosine similarity
        self.index.add(embeddings)

        # Save the index and chunks
        self._save_knowledge_base()

        logger.info(f"Knowledge base created with {len(self.chunks)} chunks")

    def _split_into_chunks(self, content: str, filename: str) -> List[str]:
        """Split content into meaningful chunks"""
        # Split by double newlines (paragraphs) or section headers
        chunks = []

        # First, split by major sections (lines starting with # or ##)
        sections = []
        current_section = []

        for line in content.split('\n'):
            if line.strip().startswith('#') and len(current_section) > 0:
                sections.append('\n'.join(current_section))
                current_section = [line]
            else:
                current_section.append(line)

        if current_section:
            sections.append('\n'.join(current_section))

        # Filter out very short chunks and clean up
        for section in sections:
            section = section.strip()
            if len(section) > 100:  # Minimum chunk size
                # Remove markdown headers for cleaner chunks
                lines = section.split('\n')
                clean_lines = []
                for line in lines:
                    if not line.strip().startswith('#'):
                        clean_lines.append(line)

                clean_section = '\n'.join(clean_lines).strip()
                if len(clean_section) > 50:  # Final check
                    chunks.append(clean_section)

        return chunks

    def _extract_topic(self, rel_path: str) -> str:
        """Extract a human-friendly topic from a relative path under the knowledge base.

        Uses a small override map for common files, otherwise derives from path and stem.
        """
        # Overrides for legacy filenames
        overrides = {
            "anatomy.txt": "Human Anatomy",
            "physiology.txt": "Human Physiology",
            "biochemistry.txt": "Medical Biochemistry",
            "pathology.txt": "Medical Pathology",
            "pharmacology.txt": "Medical Pharmacology",
        }
        key = rel_path.replace('\\', '/').lower()
        if key in overrides:
            return overrides[key]

        # Derive from directory and filename
        base = os.path.basename(rel_path)
        stem = os.path.splitext(base)[0]
        parts = []
        dir_part = os.path.dirname(rel_path)
        if dir_part and dir_part not in ('.', ''):
            # Take last directory component as high-level area
            area = os.path.basename(dir_part).replace('_', ' ').strip()
            if area:
                parts.append(area.title())
        title = stem.replace('_', ' ').replace('-', ' ').strip().title()
        if title:
            parts.append(title)
        return ' / '.join(parts) if parts else "General Medicine"

    def _knowledge_base_exists(self) -> bool:
        """Check if knowledge base files exist"""
        return os.path.exists(self.index_file) and os.path.exists(self.chunks_file)

    def _save_knowledge_base(self):
        """Save the FAISS index and chunks"""
        try:
            faiss.write_index(self.index, self.index_file)

            # Save chunks and metadata
            with open(self.chunks_file, 'wb') as f:
                pickle.dump({
                    'chunks': self.chunks,
                    'metadata': self.chunk_metadata
                }, f)

            logger.info("Knowledge base saved successfully")
        except Exception as e:
            logger.error(f"Error saving knowledge base: {str(e)}")

    def _load_knowledge_base(self):
        """Load the FAISS index and chunks"""
        try:
            logger.info("Loading existing knowledge base...")

            # Load FAISS index
            self.index = faiss.read_index(self.index_file)

            # Load chunks and metadata
            with open(self.chunks_file, 'rb') as f:
                data = pickle.load(f)
                self.chunks = data['chunks']
                self.chunk_metadata = data['metadata']

            logger.info(f"Knowledge base loaded with {len(self.chunks)} chunks")
        except Exception as e:
            logger.error(f"Error loading knowledge base: {str(e)}")
            raise

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, any]]:
        """
        Retrieve most relevant chunks for a query

        Args:
            query: Search query
            top_k: Number of top results to return

        Returns:
            List of dictionaries with chunk content and metadata
        """
        if not self.embedding_model or not self.index:
            raise ValueError("Knowledge base not initialized")

        try:
            # Encode the query
            query_embedding = self.embedding_model.encode([query])
            faiss.normalize_L2(query_embedding)

            # Search the index
            scores, indices = self.index.search(query_embedding, top_k)

            # Prepare results
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.chunks):  # Valid index
                    result = {
                        "content": self.chunks[idx],
                        "score": float(scores[0][i]),
                        "metadata": self.chunk_metadata[idx]
                    }
                    results.append(result)

            return results

        except Exception as e:
            logger.error(f"Error during retrieval: {str(e)}")
            return []

    def get_relevant_context(self, query: str, max_tokens: int = 2000) -> str:
        """
        Get relevant context for a query, formatted for AI consumption

        Args:
            query: Search query
            max_tokens: Maximum tokens in context (approximate)

        Returns:
            Formatted context string
        """
        results = self.retrieve(query, top_k=10)

        if not results:
            return ""

        # Sort by relevance score
        results.sort(key=lambda x: x['score'], reverse=True)

        # Build context
        context_parts = []
        total_length = 0

        for result in results:
            content = result['content']
            metadata = result['metadata']

            # Check if adding this chunk would exceed token limit (rough estimate)
            estimated_tokens = len(content.split()) * 1.3  # Rough token estimate
            if total_length + estimated_tokens > max_tokens:
                break

            # Format the context
            context_part = f"""
**Source**: {metadata['topic']} ({metadata['source']})
**Relevance**: {result['score']:.3f}

{content}

---
"""
            context_parts.append(context_part)
            total_length += estimated_tokens

        return "\n".join(context_parts)

    def search_by_topic(self, topic: str, limit: int = 10) -> List[Dict[str, any]]:
        """
        Search for chunks by topic

        Args:
            topic: Topic to search for
            limit: Maximum number of results

        Returns:
            List of relevant chunks
        """
        results = []
        for i, metadata in enumerate(self.chunk_metadata):
            if topic.lower() in metadata['topic'].lower():
                results.append({
                    "content": self.chunks[i],
                    "score": 1.0,  # Perfect match for topic
                    "metadata": metadata
                })

        # Sort by relevance (could be enhanced with more sophisticated scoring)
        results.sort(key=lambda x: len(x['content']), reverse=True)  # Prefer longer chunks
        return results[:limit]

    def get_statistics(self) -> Dict[str, any]:
        """Get statistics about the knowledge base"""
        return {
            "total_chunks": len(self.chunks),
            "topics": list(set(meta['topic'] for meta in self.chunk_metadata)),
            "sources": list(set(meta['source'] for meta in self.chunk_metadata)),
            "avg_chunk_length": sum(len(chunk) for chunk in self.chunks) / len(self.chunks) if self.chunks else 0
        }

# Shared singleton accessor to reuse one RAG instance across agents
_shared_rag: Optional[MedicalRAG] = None

def get_shared_rag() -> MedicalRAG:
    """Return a shared singleton instance of MedicalRAG."""
    global _shared_rag
    if _shared_rag is None:
        _shared_rag = MedicalRAG()
    return _shared_rag
