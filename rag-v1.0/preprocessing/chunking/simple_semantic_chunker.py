"""
Minimal Semantic Chunking - Just the essentials
"""

from sentence_transformers import SentenceTransformer
import re
from typing import List


class SemanticChunker:
    def __init__(
        self, 
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2", 
        threshold: float = 0.02,
        overlap_threshold: float = 0.5,  # Similarity threshold for smart overlap
        min_chunk_words: int = 250,  # Minimum chunk size in words
        max_chunk_words: int = 800   # Maximum chunk size in words
    ):
        self.model = SentenceTransformer(model_name)
        self.threshold = threshold
        self.overlap_threshold = overlap_threshold
        self.min_chunk_words = min_chunk_words
        self.max_chunk_words = max_chunk_words
    
    def chunk(self, text: str) -> List[str]:
        """Split text into semantic chunks with overlap."""
        return self._chunk_with_overlap(text)
    
    def _chunk_with_overlap(self, text: str) -> List[str]:
        """Split text into semantic chunks with sentence-level overlap."""
        # Split into sentences
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        if len(sentences) <= 1:
            return [text]
        
        # Get similarities between consecutive sentences
        embeddings = self.model.encode(sentences)
        similarities = self.model.similarity(embeddings, embeddings)
        
        # Find breakpoints where similarity drops below threshold
        breakpoints = []
        start = 0
        
        for i in range(len(sentences) - 1):
            sim = similarities[i][i + 1].item()
            if sim < self.threshold:
                breakpoints.append(i + 1)
        
        # If no breakpoints found, return whole text
        if not breakpoints:
            return [text]
        
        # Create overlapping chunks
        chunks = []
        chunk_start = 0
        
        for breakpoint in breakpoints:
            # Create chunk from start to breakpoint
            chunk_end = breakpoint
            chunk_sentences = sentences[chunk_start:chunk_end]
            chunk = ' '.join(chunk_sentences)
            chunks.append(chunk)
            
            # Smart overlap: go back while similarity is high
            overlap_start = breakpoint - 1
            while (overlap_start > chunk_start and 
                   overlap_start < len(sentences) - 1 and
                   similarities[overlap_start][overlap_start + 1].item() > self.overlap_threshold):
                overlap_start -= 1
            
            chunk_start = max(chunk_start, overlap_start)
        
        # Add final chunk
        if chunk_start < len(sentences):
            final_sentences = sentences[chunk_start:]
            final_chunk = ' '.join(final_sentences)
            chunks.append(final_chunk)
        
        # Post-process: merge tiny chunks and split oversized chunks
        chunks = self._merge_tiny_chunks(chunks)
        chunks = self._split_oversized_chunks(chunks)
        return chunks
    
    def _merge_tiny_chunks(self, chunks: List[str]) -> List[str]:
        """Merge chunks that are too small with their neighbors."""
        if len(chunks) <= 1:
            return chunks
        
        merged = []
        i = 0
        
        while i < len(chunks):
            current = chunks[i]
            word_count = len(current.split())
            
            # If current chunk is too small
            if word_count < self.min_chunk_words:
                # Try to merge with next chunk
                if i + 1 < len(chunks):
                    chunks[i + 1] = current + " " + chunks[i + 1]
                # Or merge with previous chunk
                elif merged:
                    merged[-1] = merged[-1] + " " + current
                else:
                    merged.append(current)  # Keep if it's the only chunk
            else:
                merged.append(current)
            i += 1
        
        return merged
    
    def _split_oversized_chunks(self, chunks: List[str]) -> List[str]:
        """Split chunks that are too large into smaller pieces."""
        result = []
        
        for chunk in chunks:
            word_count = len(chunk.split())
            
            if word_count <= self.max_chunk_words:
                result.append(chunk)
            else:
                # Split oversized chunk at sentence boundaries
                sentences = re.split(r'(?<=[.!?])\s+', chunk)
                current_chunk = []
                current_words = 0
                
                for sentence in sentences:
                    sentence_words = len(sentence.split())
                    
                    if current_words + sentence_words > self.max_chunk_words and current_chunk:
                        # Save current chunk and start new one
                        result.append(' '.join(current_chunk))
                        current_chunk = [sentence]
                        current_words = sentence_words
                    else:
                        current_chunk.append(sentence)
                        current_words += sentence_words
                
                # Add final chunk if any sentences remain
                if current_chunk:
                    result.append(' '.join(current_chunk))
        
        return result
