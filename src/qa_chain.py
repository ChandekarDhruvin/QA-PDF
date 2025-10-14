from langchain.prompts import PromptTemplate
from src.config import settings

def build_qa_chain(vectorstore, memory=None):
    """Build QA chain with document-focused prompting and conversation memory"""
    
    # Use OpenAI as fallback if Groq fails
    try:
        # Try to use Groq first
        from groq import Groq
        
        class GroqLLM:
            def __init__(self, api_key, model_name, temperature=0.1, max_tokens=500):
                self.client = Groq(api_key=api_key)
                self.model_name = model_name
                self.temperature = temperature
                self.max_tokens = max_tokens
            
            def __call__(self, prompt):
                try:
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=self.temperature,
                        max_tokens=self.max_tokens
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    return f"Error: {str(e)}"
        
        # Use custom Groq implementation
        llm = GroqLLM(
            api_key=settings.GROQ_API_KEY,
            model_name=settings.MODEL_NAME,
            temperature=0.1,
            max_tokens=500
        )
        
        # Build conversational chain with memory
        return build_conversational_qa_chain(vectorstore, llm, memory)
        
    except ImportError:
        # Fallback to OpenAI
        return "Currently I am not able to Response"

def build_conversational_qa_chain(vectorstore, llm, memory=None):
    """Build a conversational QA chain with memory and context handling"""
    
    # Template for handling greetings, conversation questions, and document questions
    template = """You are a helpful document analysis assistant. You can handle greetings, conversation history questions, and answer questions about the uploaded document.

INSTRUCTIONS:
1. For greetings (hi, hello, hey, etc.): Respond warmly and mention you can help with the document
2. For conversation history questions (what was my last question, what did you say before, etc.): Use the conversation history to answer
3. For document questions: Answer based ONLY on the provided context
4. If the answer is not in the context, say "I cannot find this information in the uploaded document."
5. Do NOT use general knowledge for document questions
6. Keep answers concise and clear
7. Use conversation history to maintain context and answer meta-questions about our chat

Previous conversation:
{chat_history}

Document context (if relevant):
{context}

Current question: {question}

Response:"""

    prompt = PromptTemplate(
        template=template,
        input_variables=["context", "question", "chat_history"]
    )
    
    class ConversationalQAChain:
        def __init__(self, llm, retriever, prompt, memory=None):
            self.llm = llm
            self.retriever = retriever
            self.prompt = prompt
            self.memory = memory
        
        def __call__(self, inputs):
            question = inputs.get("question", "")
            question_lower = question.lower().strip()
            
            # Determine question type
            greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
            is_greeting = question_lower in greetings
            
            conversation_patterns = [
                r"what was my (last|previous|second last|first) question",
                r"what did i ask (before|earlier|previously)",
                r"can you repeat",
                r"what did you (say|tell me) (about|before)",
                r"go back to",
                r"earlier you (said|mentioned)",
                r"in our conversation",
                r"you mentioned",
                r"we were talking about",
                r"from our chat"
            ]
            
            import re
            is_conversation_question = any(re.search(pattern, question_lower) for pattern in conversation_patterns)
            
            # Get chat history from memory
            chat_history = ""
            if self.memory:
                try:
                    history = self.memory.chat_memory.messages
                    chat_history = "\n".join([f"{msg.type}: {msg.content}" for msg in history[-10:]])
                except:
                    chat_history = ""
            
            if is_greeting:
                question_type = "greeting"
                formatted_prompt = self.prompt.format(
                    context="No document context needed for greeting",
                    question=question,
                    chat_history=chat_history
                )
                docs = []
            elif is_conversation_question:
                question_type = "conversation"
                formatted_prompt = self.prompt.format(
                    context="Use conversation history to answer this question about our chat",
                    question=question,
                    chat_history=chat_history
                )
                docs = []
            else:
                question_type = "document"
                # For document questions, retrieve relevant documents
                docs = self.retriever.get_relevant_documents(question)
                
                if not docs:
                    answer = "I cannot find this information in the uploaded document."
                    if self.memory:
                        self.memory.save_context({"input": question}, {"output": answer})
                    return {
                        "answer": answer,
                        "source_documents": [],
                        "question_type": question_type
                    }
                
                # Combine context
                context = "\n\n".join([doc.page_content for doc in docs[:4]])
                formatted_prompt = self.prompt.format(
                    context=context,
                    question=question,
                    chat_history=chat_history
                )
            
            # Get answer
            if hasattr(self.llm, '__call__'):
                answer = self.llm(formatted_prompt)
            else:
                answer = self.llm.predict(formatted_prompt)
            
            # Save to memory
            if self.memory:
                self.memory.save_context({"input": question}, {"output": answer})
            
            return {
                "answer": answer,
                "source_documents": docs[:4] if docs else [],
                "question_type": question_type
            }
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    return ConversationalQAChain(llm, retriever, prompt, memory)