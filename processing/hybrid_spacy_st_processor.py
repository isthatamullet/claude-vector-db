#!/usr/bin/env python3
"""
Hybrid spaCy + Sentence Transformers Processor
Zero-cost intelligent extraction for Claude Code Vector Database

This processor combines:
1. spaCy NER for entity extraction
2. Sentence Transformers for semantic similarity (reuses existing model)
3. Pattern templates for solution/feedback recognition
4. Confidence scoring for quality assessment
"""

import spacy
import json
import numpy as np
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

@dataclass
class HybridExtractionFields:
    """Hybrid extraction results data structure"""
    spacy_entities: str = "[]"                    # JSON: spaCy NER results
    technical_tools: str = "[]"                   # JSON: Extracted Claude Code tools  
    framework_mentions: str = "[]"                # JSON: Technology stack mentions
    solution_similarity_score: float = 0.0       # Similarity to solution patterns
    feedback_similarity_score: float = 0.0       # Similarity to feedback patterns
    error_similarity_score: float = 0.0          # Similarity to error patterns
    best_pattern_match: str = ""                  # Closest template match
    hybrid_confidence: float = 0.0               # Combined confidence score

class HybridSpacySTProcessor:
    """
    Hybrid spaCy + Sentence Transformers processor for conversation intelligence.
    
    Integrates with existing UnifiedEnhancementProcessor as Component #8.
    Uses shared embedding model for zero memory overhead.
    """
    
    def __init__(self, shared_embedding_model: Optional[Union[SentenceTransformer, None]] = None):
        """
        Initialize hybrid processor with shared model optimization.
        
        Args:
            shared_embedding_model: Pre-initialized shared model (optimization)
        """
        logger.info("🔍 Initializing Hybrid spaCy + ST Processor")
        
        # Initialize spaCy model
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("✅ spaCy English model loaded")
        except Exception as e:
            logger.error(f"❌ Failed to load spaCy model: {e}")
            raise
        
        # Use shared embedding model (memory optimization)
        if shared_embedding_model:
            self.encoder = shared_embedding_model
            logger.info("⚡ Using shared embedding model")
        else:
            # Fallback to new model if shared unavailable
            self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("🔄 Initialized new embedding model")
        
        # Initialize pattern templates for similarity matching
        self._initialize_pattern_templates()
        
        # Setup custom NER patterns for Claude Code domain
        self._setup_domain_patterns()
        
        logger.info("✅ Hybrid processor initialization complete")
    
    def _initialize_pattern_templates(self):
        """Initialize solution/feedback/error pattern templates"""
        
        # Solution pattern templates (based on existing successful patterns)
        self.solution_templates = [
            "Fixed the error by updating configuration settings and testing the changes",
            "Problem resolved after changing the code implementation and verifying functionality", 
            "Successfully implemented the solution using development tools and validation",
            "Issue solved by modifying the system configuration and running tests",
            "Error corrected through code changes and comprehensive testing validation",
            "Implementation completed using Edit tool and TypeScript compilation verification",
            "React component fixed with proper state management and performance optimization",
            "Database connection resolved through configuration updates and testing"
        ]
        
        # Feedback pattern templates (positive user responses)
        self.feedback_templates = [
            "That worked perfectly, thank you for the solution",
            "Great solution, problem is completely resolved now", 
            "Perfect fix, everything is working exactly as expected",
            "Excellent approach, issue is solved and tested successfully",
            "This solution works great, no more errors occurring",
            "Outstanding work, the implementation is functioning perfectly",
            "Brilliant fix, all functionality restored and optimized",
            "Fantastic solution, system performance significantly improved"
        ]
        
        # Error pattern templates (user problem descriptions)
        self.error_templates = [
            "Getting an error when trying to run the application",
            "Something is broken and not working as expected",
            "Issue with the system causing functionality problems", 
            "Error occurred during execution and needs investigation",
            "Problem detected in the application requiring debugging",
            "TypeScript compilation errors preventing successful build",
            "React component rendering issues affecting user interface",
            "Database connection failures disrupting application flow"
        ]
        
        # Pre-compute embeddings for performance optimization
        logger.info("🧮 Computing pattern template embeddings...")
        self.solution_embeddings = self.encoder.encode(self.solution_templates)
        self.feedback_embeddings = self.encoder.encode(self.feedback_templates) 
        self.error_embeddings = self.encoder.encode(self.error_templates)
        logger.info("✅ Pattern embeddings computed and cached")
    
    def _setup_domain_patterns(self):
        """Setup spaCy patterns for Claude Code domain"""
        from spacy.matcher import Matcher
        self.matcher = Matcher(self.nlp.vocab)
        
        # Claude Code tools pattern
        claude_tools_pattern = [
            [{"TEXT": {"IN": ["Edit", "Read", "Write", "Bash", "Glob", "Grep", "TodoWrite"]}}],
            [{"TEXT": {"REGEX": r"mcp__.*"}}],  # MCP tools
            [{"LOWER": "tool"}, {"TEXT": {"REGEX": r".*"}}]
        ]
        self.matcher.add("CLAUDE_TOOL", claude_tools_pattern)
        
        # Framework/Technology patterns
        framework_patterns = [
            [{"TEXT": {"IN": ["React", "Next.js", "TypeScript", "JavaScript", "Python", "Node.js"]}}],
            [{"LOWER": {"IN": ["react", "nextjs", "typescript", "javascript", "python", "nodejs"]}}, {"TEXT": {"REGEX": r"\.js|\.ts|\.py"}, "OP": "?"}],
            [{"TEXT": {"IN": ["HTML", "CSS", "Tailwind", "Playwright", "Jest", "Vite"]}}]
        ]
        self.matcher.add("FRAMEWORK", framework_patterns)
        
        # Success indicators pattern
        success_patterns = [
            [{"TEXT": "✅"}],
            [{"LOWER": {"IN": ["fixed", "resolved", "working", "successful", "solved", "completed"]}}],
            [{"LOWER": "no"}, {"LOWER": {"IN": ["errors", "issues", "problems"]}}],
            [{"LOWER": {"IN": ["build", "compilation", "test"]}}, {"LOWER": {"IN": ["successful", "passed", "working"]}}]
        ]
        self.matcher.add("SUCCESS_INDICATOR", success_patterns)
        
        # File reference patterns
        file_patterns = [
            [{"TEXT": {"REGEX": r".*\.(js|ts|py|html|css|json)$"}}],
            [{"TEXT": {"REGEX": r"src/.*"}}, {"TEXT": {"REGEX": r".*"}, "OP": "?"}],
            [{"TEXT": {"REGEX": r"\.\/.*"}}]
        ]
        self.matcher.add("FILE_REFERENCE", file_patterns)
    
    def extract_intelligence(self, content: str) -> Dict[str, Any]:
        """
        Main extraction method - combines spaCy NER + Sentence Transformer similarity.
        
        Args:
            content: Conversation content to analyze
            
        Returns:
            Dictionary with hybrid extraction results
        """
        if len(content) < 20:  # Skip very short content
            return self._empty_result()
        
        try:
            # Stage 1: spaCy NER + Pattern Matching
            spacy_results = self._extract_spacy_intelligence(content)
            
            # Stage 2: Semantic Similarity Analysis
            similarity_results = self._calculate_semantic_similarities(content)
            
            # Stage 3: Combine and score results
            combined_results = self._combine_extraction_results(spacy_results, similarity_results)
            
            return combined_results
            
        except Exception as e:
            logger.warning(f"Hybrid extraction failed for content: {e}")
            return self._empty_result()
    
    def _extract_spacy_intelligence(self, content: str) -> Dict[str, Any]:
        """Extract intelligence using spaCy NER and custom patterns"""
        
        # Process content with spaCy
        doc = self.nlp(content)
        
        # Extract named entities
        spacy_entities = []
        for ent in doc.ents:
            spacy_entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
                "confidence": 0.8  # spaCy doesn't provide confidence, use default
            })
        
        # Extract custom patterns
        matches = self.matcher(doc)
        technical_tools = []
        framework_mentions = []
        file_references = []
        success_indicators = []
        
        for match_id, start, end in matches:
            span = doc[start:end]
            label = self.nlp.vocab.strings[match_id]
            
            if label == "CLAUDE_TOOL":
                technical_tools.append(span.text)
            elif label == "FRAMEWORK":
                framework_mentions.append(span.text)
            elif label == "FILE_REFERENCE":
                file_references.append(span.text)
            elif label == "SUCCESS_INDICATOR":
                success_indicators.append(span.text)
        
        return {
            "spacy_entities": spacy_entities,
            "technical_tools": list(set(technical_tools)),  # Remove duplicates
            "framework_mentions": list(set(framework_mentions)),
            "file_references": list(set(file_references)),
            "success_indicators": success_indicators
        }
    
    def _calculate_semantic_similarities(self, content: str) -> Dict[str, Any]:
        """Calculate semantic similarities to pattern templates"""
        
        # Encode content
        content_embedding = self.encoder.encode([content])
        
        # Calculate similarities to each template category
        solution_similarities = np.dot(content_embedding, self.solution_embeddings.T)[0]
        feedback_similarities = np.dot(content_embedding, self.feedback_embeddings.T)[0] 
        error_similarities = np.dot(content_embedding, self.error_embeddings.T)[0]
        
        # Find best matches
        best_solution_idx = np.argmax(solution_similarities)
        best_feedback_idx = np.argmax(feedback_similarities)
        best_error_idx = np.argmax(error_similarities)
        
        solution_score = float(solution_similarities[best_solution_idx])
        feedback_score = float(feedback_similarities[best_feedback_idx])
        error_score = float(error_similarities[best_error_idx])
        
        # Determine overall best pattern match
        scores = {"solution": solution_score, "feedback": feedback_score, "error": error_score}
        best_pattern_type = max(scores, key=scores.get)
        best_score = scores[best_pattern_type]
        
        if best_pattern_type == "solution":
            best_pattern_match = self.solution_templates[best_solution_idx]
        elif best_pattern_type == "feedback":
            best_pattern_match = self.feedback_templates[best_feedback_idx]  
        else:
            best_pattern_match = self.error_templates[best_error_idx]
        
        return {
            "solution_similarity_score": solution_score,
            "feedback_similarity_score": feedback_score,
            "error_similarity_score": error_score,
            "best_pattern_match": best_pattern_match,
            "best_pattern_type": best_pattern_type,
            "best_score": best_score
        }
    
    def _combine_extraction_results(self, spacy_results: Dict, similarity_results: Dict) -> Dict[str, Any]:
        """Combine spaCy and similarity results into final extraction"""
        
        # Calculate hybrid confidence score
        entity_confidence = min(len(spacy_results["spacy_entities"]) / 5.0, 1.0)  # More entities = higher confidence
        similarity_confidence = similarity_results["best_score"]
        tool_confidence = min(len(spacy_results["technical_tools"]) / 3.0, 1.0)  # Tool extraction bonus
        
        hybrid_confidence = (entity_confidence + similarity_confidence + tool_confidence) / 3
        
        # Format results for ChromaDB storage
        return {
            "spacy_entities": json.dumps(spacy_results["spacy_entities"]),
            "technical_tools": json.dumps(spacy_results["technical_tools"]),
            "framework_mentions": json.dumps(spacy_results["framework_mentions"]),
            "solution_similarity_score": similarity_results["solution_similarity_score"],
            "feedback_similarity_score": similarity_results["feedback_similarity_score"],
            "error_similarity_score": similarity_results["error_similarity_score"],
            "best_pattern_match": similarity_results["best_pattern_match"],
            "hybrid_confidence": min(hybrid_confidence, 1.0)  # Cap at 1.0
        }
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result for error cases or short content"""
        return {
            "spacy_entities": "[]",
            "technical_tools": "[]", 
            "framework_mentions": "[]",
            "solution_similarity_score": 0.0,
            "feedback_similarity_score": 0.0,
            "error_similarity_score": 0.0,
            "best_pattern_match": "",
            "hybrid_confidence": 0.0
        }
    
    def get_processor_stats(self) -> Dict[str, Any]:
        """Get processor statistics and health info"""
        return {
            "processor_name": "HybridSpacySTProcessor",
            "spacy_model": "en_core_web_sm",
            "embedding_model": "all-MiniLM-L6-v2",
            "pattern_templates": {
                "solution_patterns": len(self.solution_templates),
                "feedback_patterns": len(self.feedback_templates),
                "error_patterns": len(self.error_templates)
            },
            "domain_patterns": {
                "claude_tools": "CLAUDE_TOOL",
                "frameworks": "FRAMEWORK", 
                "success_indicators": "SUCCESS_INDICATOR",
                "file_references": "FILE_REFERENCE"
            },
            "status": "healthy",
            "shared_model_used": hasattr(self, 'encoder')
        }

# Export for easy importing
__all__ = ['HybridSpacySTProcessor', 'HybridExtractionFields']