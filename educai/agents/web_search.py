"""
Web Search Agent with Fact Verification for Medical Information
This agent searches the web for medical information and verifies its accuracy
"""

import os
import requests
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv
from educai.config import GEMINI_FAST_MODEL

load_dotenv()

class WebSearchAgent:
    """Agent for searching web and verifying medical information"""
    
    def __init__(self):
        self.serper_api_key = os.getenv('SERPER_API_KEY')  # Serper.dev for Google Search
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel(GEMINI_FAST_MODEL)
        else:
            self.model = None
    
    def search_web(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search the web using Serper.dev Google Search API
        Returns list of search results with title, link, snippet
        """
        if not self.serper_api_key:
            # Fallback: return empty results if no API key
            return []
        
        url = "https://google.serper.dev/search"
        
        # Add medical context to query
        medical_query = f"{query} site:ncbi.nlm.nih.gov OR site:nih.gov OR site:who.int OR site:mayoclinic.org OR site:medlineplus.gov"
        
        payload = {
            "q": medical_query,
            "num": num_results
        }
        
        headers = {
            'X-API-KEY': self.serper_api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            results = []
            if 'organic' in data:
                for result in data['organic'][:num_results]:
                    results.append({
                        'title': result.get('title', ''),
                        'link': result.get('link', ''),
                        'snippet': result.get('snippet', ''),
                        'source': self._extract_domain(result.get('link', ''))
                    })
            
            return results
            
        except Exception as e:
            print(f"Error in web search: {str(e)}")
            return []
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain name from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return url
    
    def verify_information(self, question: str, search_results: List[Dict[str, Any]], 
                          proposed_answer: str) -> Dict[str, Any]:
        """
        Verify the accuracy of information using AI and multiple sources
        Returns verification result with confidence score
        """
        if not search_results:
            return {
                'verified': False,
                'confidence': 0.0,
                'reason': 'No search results to verify against',
                'reliable_sources': []
            }
        if not self.model:
            # Fallback if model not available
            return {
                'verified': False,
                'status': 'NOT_VERIFIED',
                'confidence': 0.0,
                'reliable_sources': [r.get('source') for r in search_results[:3] if r.get('source')],
                'concerns': 'AI model unavailable for verification',
                'recommendation': 'Cross-check with reliable medical sources',
                'source_urls': [r['link'] for r in search_results[:3]]
            }
        
        # Compile evidence from search results
        evidence = "\n\n".join([
            f"Source {i+1} ({result['source']}):\nTitle: {result['title']}\nContent: {result['snippet']}"
            for i, result in enumerate(search_results)
        ])
        
        # Create verification prompt
        verification_prompt = f"""You are a medical fact-checker. Verify the accuracy of the following medical information.

QUESTION: {question}

PROPOSED ANSWER: {proposed_answer}

EVIDENCE FROM RELIABLE MEDICAL SOURCES:
{evidence}

Your task:
1. Cross-reference the proposed answer with the evidence from reliable sources
2. Check for any contradictions or inaccuracies
3. Assess the reliability of the sources (prioritize .gov, .edu, WHO, NIH, PubMed)
4. Provide a confidence score (0-100%)

Respond in this exact format:
VERIFICATION: [VERIFIED/NOT_VERIFIED/PARTIALLY_VERIFIED]
CONFIDENCE: [0-100]
RELIABLE_SOURCES: [List source names that support this information]
CONCERNS: [Any red flags, contradictions, or missing context]
RECOMMENDATION: [Brief recommendation on how to use this information]
"""
        
        try:
            # Use Gemini to verify
            response = self.model.generate_content(verification_prompt)
            verification_text = response.text
            
            # Parse verification response
            result = self._parse_verification_response(verification_text, search_results)
            return result
            
        except Exception as e:
            print(f"Error in verification: {str(e)}")
            return {
                'verified': False,
                'confidence': 0.0,
                'reason': f'Verification failed: {str(e)}',
                'reliable_sources': []
            }
    
    def _parse_verification_response(self, response: str, 
                                    search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse the AI verification response"""
        lines = response.split('\n')
        
        verification_status = 'NOT_VERIFIED'
        confidence = 0.0
        reliable_sources = []
        concerns = ''
        recommendation = ''
        
        for line in lines:
            line = line.strip()
            if line.startswith('VERIFICATION:'):
                verification_status = line.split(':', 1)[1].strip()
            elif line.startswith('CONFIDENCE:'):
                try:
                    confidence_str = line.split(':', 1)[1].strip().replace('%', '')
                    confidence = float(confidence_str)
                except:
                    confidence = 0.0
            elif line.startswith('RELIABLE_SOURCES:'):
                sources_str = line.split(':', 1)[1].strip()
                reliable_sources = [s.strip() for s in sources_str.split(',') if s.strip()]
            elif line.startswith('CONCERNS:'):
                concerns = line.split(':', 1)[1].strip()
            elif line.startswith('RECOMMENDATION:'):
                recommendation = line.split(':', 1)[1].strip()
        
        verified = verification_status in ['VERIFIED', 'PARTIALLY_VERIFIED']
        
        return {
            'verified': verified,
            'status': verification_status,
            'confidence': confidence,
            'reliable_sources': reliable_sources,
            'concerns': concerns,
            'recommendation': recommendation,
            'source_urls': [r['link'] for r in search_results[:3]]  # Top 3 URLs
        }
    
    def get_verified_answer(self, question: str, 
                           context_available: bool = False) -> Dict[str, Any]:
        """
        Main method: Search web, get answer, and verify it
        Returns verified answer with sources
        """
        # Search the web
        search_results = self.search_web(question)
        
        if not search_results:
            return {
                'success': False,
                'answer': None,
                'error': 'No reliable search results found',
                'sources': []
            }
        
        # Generate answer from search results
        answer = self._generate_answer_from_sources(question, search_results)
        
        # Verify the answer
        verification = self.verify_information(question, search_results, answer)
        
        # Only return if verified with high confidence
        if verification['verified'] and verification['confidence'] >= 70:
            return {
                'success': True,
                'answer': answer,
                'verification': verification,
                'sources': search_results[:3],  # Top 3 sources
                'confidence': verification['confidence'],
                'web_search_used': True
            }
        else:
            return {
                'success': False,
                'answer': answer,
                'verification': verification,
                'error': f"Information could not be verified with sufficient confidence ({verification['confidence']}%)",
                'sources': search_results[:3],
                'web_search_used': True
            }
    
    def _generate_answer_from_sources(self, question: str, 
                                     search_results: List[Dict[str, Any]]) -> str:
        """Generate a comprehensive answer from search results"""
        # Compile information from sources
        sources_text = "\n\n".join([
            f"Source: {result['source']}\n{result['snippet']}"
            for result in search_results
        ])
        
        prompt = f"""Based on the following reliable medical sources, provide a comprehensive, accurate answer to the question.

QUESTION: {question}

INFORMATION FROM RELIABLE SOURCES:
{sources_text}

Provide a clear, accurate, and well-structured answer based ONLY on the information from these sources. 
If there are conflicting information, mention it. Focus on medical accuracy.

Answer:"""
        
        try:
            if not self.model:
                raise RuntimeError('Model unavailable')
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            # Fallback: combine snippets
            return "\n\n".join([r['snippet'] for r in search_results[:2]])
    
    def check_knowledge_gap(self, question: str, rag_context: str) -> bool:
        """
        Determine if RAG context is insufficient and web search is needed
        Returns True if web search is recommended
        """
        if not rag_context or len(rag_context.strip()) < 50:
            return True  # Very little or no context
        
        prompt = f"""Determine if the following context is sufficient to answer the question accurately.

QUESTION: {question}

AVAILABLE CONTEXT:
{rag_context[:500]}...

Respond with only one word: SUFFICIENT or INSUFFICIENT"""
        
        try:
            if not self.model:
                return False
            response = self.model.generate_content(prompt)
            decision = response.text.strip().upper()
            return 'INSUFFICIENT' in decision
        except:
            return False  # Default to not using web search if check fails
