# Efficient output-focused guardrail system
import re

# Only block truly harmful inputs
HARMFUL_TERMS = {"hack", "exploit", "illegal", "suicide", "self-harm"}
HARMFUL_PATTERNS = [
    r"how to (hack|break|exploit|steal)",
    r"generate (fake|false) (documents|ids|certificates)",
    r"illegal (activities|methods|ways)"
]

def validate_safety(question):
    """Only validate for safety - let everything else through"""
    question_lower = question.lower().strip()
    
    # Block only harmful content
    if any(term in question_lower for term in HARMFUL_TERMS):
        return False, "I can't help with potentially harmful requests."
    
    for pattern in HARMFUL_PATTERNS:
        if re.search(pattern, question_lower):
            return False, "I can't assist with potentially harmful requests."
    
    # Block empty questions
    if len(question.strip()) < 2:
        return False, "Please ask a question."
    
    return True, None

def validate_output_quality(answer, source_documents, question, question_type="document"):
    """
    Smart output validation based on question type
    Returns (is_valid, processed_answer)
    """
    answer_lower = answer.lower().strip()
    
    # For conversation/greeting questions, minimal validation
    if question_type in ["greeting", "conversation"]:
        return True, enforce_output_format(answer)
    
    # For document questions, validate against source
    if question_type == "document":
        # Check if we have source documents
        if not source_documents:
            return False, "I cannot find this information in the uploaded document."
        
        # Check for obvious general knowledge responses
        general_knowledge_indicators = [
            "based on my general knowledge",
            "as an ai language model", 
            "in general,",
            "typically,",
            "usually,",
            "commonly,",
            "is a programming language",
            "is defined as",
            "refers to the",
            "in computer science"
        ]
        
        if any(indicator in answer_lower for indicator in general_knowledge_indicators):
            return False, "I can only answer based on the uploaded document content."
        
        # Simple overlap check - if answer has some connection to source, it's probably valid
        if source_documents:
            source_text = " ".join([doc.page_content.lower() for doc in source_documents[:2]])
            answer_words = set(answer_lower.split())
            source_words = set(source_text.split())
            overlap = len(answer_words.intersection(source_words))
            
            # Very lenient check - just need some overlap
            if len(answer_words) > 10 and overlap < 2:
                return False, "I can only answer based on the uploaded document content."
    
    return True, enforce_output_format(answer)

def enforce_output_format(answer):
    """Enforce clear and concise output format"""
    # Remove common LLM hedging language
    hedging_phrases = [
        "I might be wrong, ",
        "I could be mistaken, ",
        "Based on my training, ",
        "As an AI, ",
        "According to my knowledge, ",
        "From what I understand, "
    ]
    
    cleaned_answer = answer
    for phrase in hedging_phrases:
        cleaned_answer = cleaned_answer.replace(phrase, "")
    
    # Ensure answer starts with capital letter
    cleaned_answer = cleaned_answer.strip()
    if cleaned_answer and not cleaned_answer[0].isupper():
        cleaned_answer = cleaned_answer[0].upper() + cleaned_answer[1:]
    
    # Limit to reasonable length (150 words max for conciseness)
    words = cleaned_answer.split()
    if len(words) > 150:
        cleaned_answer = " ".join(words[:150]) + "..."
    
    # Ensure it ends with proper punctuation
    if cleaned_answer and cleaned_answer[-1] not in '.!?':
        cleaned_answer += "."
    
    return cleaned_answer
