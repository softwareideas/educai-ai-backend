"""
Rebuild the medical knowledge base with updated content
"""
import os
import sys

# Delete old index files if they exist
if os.path.exists('medical_index.faiss'):
    os.remove('medical_index.faiss')
    print("✓ Removed old medical_index.faiss")

if os.path.exists('medical_chunks.pkl'):
    os.remove('medical_chunks.pkl')
    print("✓ Removed old medical_chunks.pkl")

# Import and rebuild the RAG system
from educai.agents.rag import MedicalRAG

print("\n🔄 Rebuilding medical knowledge base...")
print("=" * 60)

rag = MedicalRAG(knowledge_base_path="knowledge_base")

print("=" * 60)
print("\n✅ Knowledge base rebuilt successfully!")

# Display statistics
stats = rag.get_statistics()
print("\n📊 Knowledge Base Statistics:")
print(f"   • Total chunks: {stats['total_chunks']}")
print(f"   • Average chunk length: {stats['avg_chunk_length']:.0f} characters")
print(f"   • Topics covered: {len(stats['topics'])}")
print(f"   • Sources: {len(stats['sources'])}")

print("\n📚 Topics:")
for topic in stats['topics']:
    print(f"   • {topic}")

print("\n🎉 Your AI medical tutor is now loaded with comprehensive NEET-focused content!")
