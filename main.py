
import os
import chainlit as cl
import google.generativeai as genai
from dotenv import load_dotenv
import asyncio
from typing import Optional

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=gemini_api_key)

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=genai.types.GenerationConfig(
        temperature=0.7,
        top_p=0.8,
        top_k=40,
        max_output_tokens=2048,
    )
)

@cl.on_chat_start
async def handle_chat_start():
    """Initialize the chat session with a personalized greeting"""
    
    # Set user session
    cl.user_session.set("conversation_count", 0)
    
    # Send welcome message with better formatting
    welcome_message = """
    السلام علیکم! 🤖✨
    
    Welcome to your **Gemini AI Assistant**! I'm powered by Google's latest AI technology , I'm develop by Haider Hussain and I'm here to help you with:
    
    • **Questions & Research** 🔍
    • **Creative Writing** ✍️  
    • **Problem Solving** 🧠
    • **Code & Technical Help** 💻
    • **General Conversation** 💬
    
    How can I assist you today?
    """
    
    await cl.Message(
        content=welcome_message,
        author="Gemini Assistant"
    ).send()

@cl.on_message
async def handle_message(message: cl.Message):
    """Handle incoming messages with enhanced UX"""
    
    # Get conversation count
    conversation_count = cl.user_session.get("conversation_count", 0)
    cl.user_session.set("conversation_count", conversation_count + 1)
    
    # Show typing indicator
    async with cl.Step(name="thinking", type="tool") as step:
        step.output = "🤔 Processing your request..."
        
        try:
            # Generate response
            prompt = message.content
            response = model.generate_content(prompt)
            
            # Extract response text
            response_text = response.text if hasattr(response, "text") else "I apologize, but I couldn't generate a response. Please try again."
            
            step.output = "✅ Response generated successfully!"
            
        except Exception as e:
            response_text = f"❌ I encountered an error: {str(e)}. Please try again or rephrase your question."
            step.output = f"❌ Error: {str(e)}"
    
    # Send the response with better formatting
    await cl.Message(
        content=response_text,
        author="Gemini Assistant"
    ).send()
    
    # Add helpful suggestions after certain number of messages
    if conversation_count > 0 and conversation_count % 5 == 0:
        suggestions = [
            "💡 Try asking me about a specific topic you're curious about",
            "🎨 I can help with creative writing projects",
            "🔧 Need help with coding or technical questions?",
            "📚 Want to learn something new? Just ask!"
        ]
        
        suggestion_msg = f"""
        ---
        **Suggestion #{conversation_count//5}**: {suggestions[(conversation_count//5-1) % len(suggestions)]}
        """
        
        await cl.Message(
            content=suggestion_msg,
            author="Assistant Tips"
        ).send()

@cl.on_chat_end
async def handle_chat_end():
    """Handle chat end with a goodbye message"""
    await cl.Message(
        content="خدا حافظ! Thanks for chatting with me. Feel free to start a new conversation anytime! 👋",
        author="Gemini Assistant"
    ).send()

# Optional: Add error handling for startup
@cl.on_settings_update
async def setup_agent(settings):
    """Handle settings updates"""
    print("Settings updated:", settings)