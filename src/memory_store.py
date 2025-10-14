# src/memory_store.py
try:
    from langchain_community.memory import ConversationBufferWindowMemory
except ImportError:
    from langchain.memory import ConversationBufferWindowMemory

def create_session_memory(max_token_limit=1000):
    """Create a new memory instance for a session with token limit"""
    return ConversationBufferWindowMemory(
        memory_key="chat_history",
        return_messages=True,
        k=10,  # Keep last 10 exchanges
        max_token_limit=max_token_limit
    )

def get_conversation_context(memory, max_exchanges=3):
    """Get formatted conversation context for the LLM"""
    if not memory or not hasattr(memory, 'chat_memory'):
        return ""
    
    try:
        messages = memory.chat_memory.messages
        if not messages:
            return ""
        
        # Get last few exchanges
        recent_messages = messages[-(max_exchanges * 2):]  # Each exchange = user + assistant
        
        context_parts = []
        for msg in recent_messages:
            role = "User" if msg.type == "human" else "Assistant"
            context_parts.append(f"{role}: {msg.content}")
        
        return "\n".join(context_parts)
    except Exception:
        return ""
