import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import requests
from urllib.parse import urlparse
from loguru import logger


class KnowledgeBaseLoader:
    """Loads and manages knowledge base content for clients."""
    
    def __init__(self):
        self._cache: Dict[str, str] = {}
    
    def load_knowledge_base(self, kb_config: Dict[str, str]) -> str:
        """Load knowledge base content based on configuration."""
        if not kb_config or not kb_config.get('type') or not kb_config.get('source'):
            return ""
        
        kb_type = kb_config['type'].lower()
        source = kb_config['source']
        
        # Check cache first
        cache_key = f"{kb_type}:{source}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            if kb_type == 'file':
                content = self._load_from_file(source)
            elif kb_type == 'url':
                content = self._load_from_url(source)
            elif kb_type == 'text':
                content = source  # Direct text content
            else:
                logger.warning(f"Unknown knowledge base type: {kb_type}")
                return ""
            
            # Cache the content
            self._cache[cache_key] = content
            logger.info(f"✅ Loaded knowledge base ({kb_type}): {len(content)} characters")
            return content
            
        except Exception as e:
            logger.error(f"❌ Failed to load knowledge base ({kb_type}: {source}): {e}")
            return ""
    
    def _load_from_file(self, file_path: str) -> str:
        """Load knowledge base from a local file."""
        path = Path(file_path)
        
        # Support relative paths from knowledge_bases directory
        if not path.is_absolute():
            kb_dir = Path("knowledge_bases")
            kb_dir.mkdir(exist_ok=True)
            path = kb_dir / file_path
        
        if not path.exists():
            raise FileNotFoundError(f"Knowledge base file not found: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Handle different file types
        if path.suffix.lower() == '.json':
            # If it's JSON, try to extract relevant fields
            try:
                data = json.loads(content)
                if isinstance(data, dict):
                    # Extract common fields that might contain knowledge
                    knowledge_fields = ['content', 'text', 'description', 'knowledge', 'faq', 'info']
                    extracted = []
                    
                    for field in knowledge_fields:
                        if field in data:
                            extracted.append(str(data[field]))
                    
                    if extracted:
                        content = "\n\n".join(extracted)
                elif isinstance(data, list):
                    # Handle list of knowledge items
                    content = "\n\n".join(str(item) for item in data)
            except json.JSONDecodeError:
                # If JSON parsing fails, use raw content
                pass
        
        return content
    
    def _load_from_url(self, url: str) -> str:
        """Load knowledge base from a URL."""
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"Invalid URL: {url}")
        
        # Make HTTP request with timeout
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'KnowledgeBase-Loader/1.0'
        })
        response.raise_for_status()
        
        content = response.text
        
        # Handle different content types
        content_type = response.headers.get('content-type', '').lower()
        
        if 'application/json' in content_type:
            try:
                data = json.loads(content)
                if isinstance(data, dict):
                    # Extract knowledge from common JSON fields
                    knowledge_fields = ['content', 'text', 'description', 'knowledge', 'data']
                    extracted = []
                    
                    for field in knowledge_fields:
                        if field in data:
                            if isinstance(data[field], list):
                                extracted.extend(str(item) for item in data[field])
                            else:
                                extracted.append(str(data[field]))
                    
                    if extracted:
                        content = "\n\n".join(extracted)
                elif isinstance(data, list):
                    content = "\n\n".join(str(item) for item in data)
            except json.JSONDecodeError:
                pass  # Use raw content if JSON parsing fails
        
        return content
    
    def clear_cache(self):
        """Clear the knowledge base cache."""
        self._cache.clear()
        logger.info("🗑️ Knowledge base cache cleared")
    
    def get_cached_sources(self) -> List[str]:
        """Get list of currently cached knowledge base sources."""
        return list(self._cache.keys())


# Global instance
kb_loader = KnowledgeBaseLoader()


def create_knowledge_retrieval_tool(kb_content: str, brand_name: str):
    """Create a knowledge base retrieval tool for a specific client."""
    
    def search_knowledge_base(query: str) -> str:
        """Search the client's knowledge base for relevant information."""
        if not kb_content:
            return f"I don't have specific knowledge base information available. Please contact {brand_name} directly for detailed information."
        
        query_lower = query.lower()
        kb_lower = kb_content.lower()
        
        # Simple keyword matching - in production, you might want to use
        # more sophisticated methods like embeddings or vector search
        
        # Split content into paragraphs/sections
        sections = [s.strip() for s in kb_content.split('\n\n') if s.strip()]
        
        # Find sections that contain query keywords
        query_words = query_lower.split()
        relevant_sections = []
        
        for section in sections:
            section_lower = section.lower()
            # Check if section contains any query words
            matches = sum(1 for word in query_words if word in section_lower)
            if matches > 0:
                relevant_sections.append((section, matches))
        
        if not relevant_sections:
            return f"I couldn't find specific information about '{query}' in our knowledge base. Contact {brand_name} for more details."
        
        # Sort by relevance (number of matches) and take top results
        relevant_sections.sort(key=lambda x: x[1], reverse=True)
        
        # Return the most relevant section(s), keeping it concise for voice
        best_section = relevant_sections[0][0]
        
        # Truncate if too long for voice response
        if len(best_section) > 300:
            # Try to find a good breaking point
            sentences = best_section.split('. ')
            truncated = sentences[0]
            for sentence in sentences[1:]:
                if len(truncated + '. ' + sentence) < 300:
                    truncated += '. ' + sentence
                else:
                    break
            return truncated + ('.' if not truncated.endswith('.') else '')
        
        return best_section
    
    return search_knowledge_base


def validate_knowledge_base_config(kb_config: Dict[str, str]) -> tuple[bool, str]:
    """Validate knowledge base configuration."""
    if not kb_config:
        return True, "No knowledge base configured"
    
    kb_type = kb_config.get('type', '').lower()
    source = kb_config.get('source', '')
    
    if not kb_type or not source:
        return False, "Knowledge base requires both 'type' and 'source' fields"
    
    if kb_type not in ['file', 'url', 'text']:
        return False, f"Invalid knowledge base type: {kb_type}. Must be 'file', 'url', or 'text'"
    
    if kb_type == 'file':
        path = Path(source)
        if not path.is_absolute():
            kb_dir = Path("knowledge_bases")
            path = kb_dir / source
        
        if not path.exists():
            return False, f"Knowledge base file not found: {path}"
    
    elif kb_type == 'url':
        parsed = urlparse(source)
        if not parsed.scheme or not parsed.netloc:
            return False, f"Invalid URL: {source}"
    
    elif kb_type == 'text':
        if len(source) < 10:
            return False, "Text knowledge base content too short (minimum 10 characters)"
    
    return True, "Knowledge base configuration is valid"