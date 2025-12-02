"""
Pharma Agentic AI - Streamlit Frontend
Professional chat interface with authentication, conversation memory, and rate limiting.
"""
import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Initialize database on first import
try:
    from src.database.db import init_database
    init_database()
except Exception:
    pass

# Page config
st.set_page_config(
    page_title="Pharma Agentic AI",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a365d;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #718096;
        margin-top: 0;
        margin-bottom: 1.5rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 8px;
    }
    .agent-tag {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 500;
        margin: 2px;
        background: #e2e8f0;
        color: #2d3748;
    }
    .status-bar {
        background: linear-gradient(90deg, #1a365d 0%, #2b6cb0 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 8px;
        font-size: 0.85rem;
        margin-bottom: 1rem;
    }
    div[data-testid="stSidebar"] {
        background-color: #f8fafc;
    }
    .footer {
        text-align: center;
        color: #a0aec0;
        font-size: 0.8rem;
        padding: 1rem 0;
    }
    .user-badge {
        background: #48bb78;
        color: white;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.8rem;
    }
    .rate-limit-bar {
        background: #edf2f7;
        border-radius: 4px;
        height: 6px;
        margin-top: 4px;
    }
    .rate-limit-fill {
        background: #4299e1;
        height: 100%;
        border-radius: 4px;
        transition: width 0.3s;
    }
    .error-box {
        background: #fed7d7;
        border: 1px solid #fc8181;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
    }
    .success-box {
        background: #c6f6d5;
        border: 1px solid #68d391;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
    }
    .history-item {
        padding: 8px 12px;
        border-radius: 6px;
        margin: 4px 0;
        cursor: pointer;
        border: 1px solid #e2e8f0;
    }
    .history-item:hover {
        background: #edf2f7;
    }
</style>
""", unsafe_allow_html=True)


def init_session():
    """Initialize session state."""
    defaults = {
        "messages": [],
        "last_response": None,
        "last_agents": [],
        "last_query": "",
        # Auth
        "logged_in": False,
        "user": None,
        "session_token": None,
        # Conversation
        "conversation_id": None,
        "show_history": False,
        # UI state
        "show_login": True,
        "error_message": None,
        "success_message": None
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def show_error(message: str):
    """Display error message."""
    st.markdown(f'<div class="error-box">❌ {message}</div>', unsafe_allow_html=True)


def show_success(message: str):
    """Display success message."""
    st.markdown(f'<div class="success-box">✅ {message}</div>', unsafe_allow_html=True)


def login_page():
    """Render login/register page."""
    st.markdown('<p class="main-header">💊 Pharma Agentic AI</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Multi-Agent Intelligence for Pharmaceutical Strategy</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2, tab3 = st.tabs(["🔐 Login", "📝 Register", "👤 Demo"])
        
        with tab1:
            st.markdown("### Sign In")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", use_container_width=True, type="primary"):
                if username and password:
                    try:
                        from src.services.auth import AuthService
                        token, user_info, message = AuthService.login(username, password)
                        
                        if token:
                            st.session_state.logged_in = True
                            st.session_state.user = user_info
                            st.session_state.session_token = token
                            
                            # Load most recent conversation
                            try:
                                from src.services.conversation import ConversationService
                                conversations = ConversationService.get_user_conversations(user_info["id"], limit=1)
                                if conversations:
                                    recent = ConversationService.get_conversation(conversations[0]["id"])
                                    if recent and recent["messages"]:
                                        st.session_state.conversation_id = recent["id"]
                                        st.session_state.messages = [
                                            {"role": m["role"], "content": m["content"], "agents": m.get("agents", [])}
                                            for m in recent["messages"]
                                        ]
                            except Exception:
                                pass  # Start fresh if loading fails
                            
                            st.rerun()
                        else:
                            show_error(message)
                    except Exception as e:
                        show_error(f"Login failed: {str(e)}")
                else:
                    show_error("Please enter username and password")
        
        with tab2:
            st.markdown("### Create Account")
            new_username = st.text_input("Username", key="reg_username")
            new_email = st.text_input("Email", key="reg_email")
            new_password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
            
            if st.button("Register", use_container_width=True):
                if new_password != confirm_password:
                    show_error("Passwords don't match")
                elif not all([new_username, new_email, new_password]):
                    show_error("Please fill all fields")
                else:
                    try:
                        from src.services.auth import AuthService
                        success, message = AuthService.register(new_username, new_email, new_password)
                        
                        if success:
                            show_success(message + " Please login.")
                        else:
                            show_error(message)
                    except Exception as e:
                        show_error(f"Registration failed: {str(e)}")
        
        with tab3:
            st.markdown("### Quick Demo Access")
            st.info("Try the system without creating an account")
            
            demo_accounts = [
                ("demo", "demo", "Analyst"),
                ("analyst", "analyst123", "Analyst"),
                ("manager", "manager123", "Manager"),
            ]
            
            for username, password, role in demo_accounts:
                if st.button(f"Login as {role} ({username})", key=f"demo_{username}", use_container_width=True):
                    try:
                        from src.services.auth import AuthService
                        token, user_info, message = AuthService.login(username, password)
                        
                        if token:
                            st.session_state.logged_in = True
                            st.session_state.user = user_info
                            st.session_state.session_token = token
                            
                            # Load most recent conversation
                            try:
                                from src.services.conversation import ConversationService
                                conversations = ConversationService.get_user_conversations(user_info["id"], limit=1)
                                if conversations:
                                    recent = ConversationService.get_conversation(conversations[0]["id"])
                                    if recent and recent["messages"]:
                                        st.session_state.conversation_id = recent["id"]
                                        st.session_state.messages = [
                                            {"role": m["role"], "content": m["content"], "agents": m.get("agents", [])}
                                            for m in recent["messages"]
                                        ]
                            except Exception:
                                pass  # Start fresh if loading fails
                            
                            st.rerun()
                        else:
                            show_error(f"Demo login failed: {message}")
                    except Exception as e:
                        show_error(f"Demo login failed: {str(e)}")


def sidebar():
    """Render sidebar."""
    with st.sidebar:
        # User info
        if st.session_state.logged_in and st.session_state.user:
            user = st.session_state.user
            st.markdown(f"**👤 {user['username']}**")
            st.caption(f"Role: {user['role'].title()}")
            
            if st.button("🚪 Logout", use_container_width=True):
                try:
                    from src.services.auth import AuthService
                    AuthService.logout(st.session_state.session_token)
                except:
                    pass
                st.session_state.logged_in = False
                st.session_state.user = None
                st.session_state.session_token = None
                st.session_state.messages = []
                st.session_state.conversation_id = None
                st.rerun()
            
            st.markdown("---")
        
        # Conversation history
        st.markdown("### 💬 Conversations")
        
        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.conversation_id = None
            st.session_state.last_response = None
            st.rerun()
        
        # Show recent conversations
        if st.session_state.logged_in and st.session_state.user:
            try:
                from src.services.conversation import ConversationService
                user_id = st.session_state.user["id"]
                conversations = ConversationService.get_user_conversations(user_id, limit=10)
                
                for conv in conversations:
                    title = conv["title"][:30] + "..." if len(conv["title"]) > 30 else conv["title"]
                    if st.button(f"📄 {title}", key=f"conv_{conv['id']}", use_container_width=True):
                        # Load conversation
                        full_conv = ConversationService.get_conversation(conv["id"])
                        if full_conv:
                            st.session_state.conversation_id = conv["id"]
                            st.session_state.messages = [
                                {"role": m["role"], "content": m["content"], "agents": m.get("agents", [])}
                                for m in full_conv["messages"]
                            ]
                            st.rerun()
            except Exception as e:
                st.caption(f"Could not load history")
        
        st.markdown("---")
        
        # Agents info
        st.markdown("### 🤖 Agents")
        agents_info = [
            ("📊 Market", "IQVIA data, market size"),
            ("📜 Patent", "IP landscape, expiry"),
            ("🚢 Trade", "Import/export data"),
            ("🔬 Clinical", "Trials, pipeline"),
            ("💬 Patient", "Sentiment, complaints"),
            ("⚔️ Competitor", "War gaming"),
            ("📁 Internal", "Strategy docs"),
            ("🌐 Web", "Real-time news"),
            ("🤖 AI", "General knowledge"),
        ]
        for name, desc in agents_info:
            st.caption(f"**{name}** — {desc}")
        
        st.markdown("---")
        
        # Rate limit status
        st.markdown("### 📊 API Usage")
        try:
            from src.services.rate_limiter import RateLimiter
            stats = RateLimiter.get_usage_stats()
            
            for api, data in stats.items():
                used = data.get("global_calls", 0)
                limit = data.get("global_limit", 100)
                pct = min(100, int((used / limit) * 100)) if limit > 0 else 0
                color = "#48bb78" if pct < 70 else "#ecc94b" if pct < 90 else "#fc8181"
                
                st.caption(f"**{api.title()}**: {used}/{limit}")
                st.markdown(
                    f'<div class="rate-limit-bar"><div class="rate-limit-fill" style="width:{pct}%;background:{color}"></div></div>',
                    unsafe_allow_html=True
                )
        except:
            st.caption("Rate limiting active")
        
        st.markdown("---")
        
        # Quick examples
        st.markdown("### 💡 Quick Examples")
        
        examples = [
            ("Whitespace", "Which respiratory diseases show low competition?"),
            ("Patent", "Check patent expiry for Sitagliptin"),
            ("Patient", "What are patients saying about injectables?"),
            ("War Game", "Simulate generic Rivaroxaban launch"),
        ]
        
        for label, query in examples:
            if st.button(label, key=f"ex_{label}", use_container_width=True):
                st.session_state.pending_query = query


def header():
    """Render header."""
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown('<p class="main-header">💊 Pharma Agentic AI</p>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">Multi-Agent Intelligence for Pharmaceutical Strategy</p>', unsafe_allow_html=True)
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.last_response = None
            st.session_state.last_agents = []
            st.session_state.conversation_id = None
            st.rerun()


def search_web(query: str) -> str:
    """Search the web using Tavily for real-time information."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Check rate limit
    try:
        from src.services.rate_limiter import RateLimiter, RateLimitExceeded
        user_id = st.session_state.user["id"] if st.session_state.user else None
        allowed, current, limit = RateLimiter.check_limit("tavily", user_id)
        
        if not allowed:
            return f"⚠️ Rate limit reached ({current}/{limit} calls today). Try again tomorrow."
    except:
        pass
    
    try:
        from tavily import TavilyClient
        
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=5,
            include_answer=True
        )
        
        # Record usage
        try:
            from src.services.rate_limiter import RateLimiter
            user_id = st.session_state.user["id"] if st.session_state.user else None
            RateLimiter.record_usage("tavily", user_id)
        except:
            pass
        
        results = []
        
        if response.get("answer"):
            results.append(f"**Summary:** {response['answer']}\n")
        
        if response.get("results"):
            results.append("**Sources:**")
            for r in response["results"][:5]:
                title = r.get("title", "No title")
                url = r.get("url", "")
                snippet = r.get("content", "")[:200]
                results.append(f"- **{title}**\n  {snippet}...\n  [Link]({url})")
        
        return "\n".join(results) if results else None
        
    except Exception as e:
        return None


def run_demo_query(query: str) -> tuple:
    """Run query using tools directly, with LLM fallback for general questions."""
    q = query.lower()
    responses = []
    agents_used = []
    
    try:
        # Market/Whitespace queries
        if any(w in q for w in ["market", "whitespace", "competition level", "cagr", "market size"]):
            from src.tools.iqvia_tool import find_low_competition_markets, query_iqvia_market
            if "respiratory" in q or "copd" in q or "ipf" in q or "asthma" in q:
                responses.append(find_low_competition_markets._run(therapy_area="Respiratory", region="India"))
            else:
                responses.append(query_iqvia_market._run(therapy_area="Oncology"))
            agents_used.append("Market")
        
        # Patent queries
        if any(w in q for w in ["patent", "expiry", "fto", "freedom to operate"]):
            from src.tools.patent_tool import check_patent_expiry, query_patents
            if "sitagliptin" in q:
                responses.append(check_patent_expiry._run(molecule="Sitagliptin", country="US"))
            elif "pembrolizumab" in q:
                responses.append(query_patents._run(molecule="Pembrolizumab"))
            else:
                responses.append(check_patent_expiry._run(molecule="Rivaroxaban", country="US"))
            agents_used.append("Patent")
        
        # Clinical/Repurposing queries
        if any(w in q for w in ["trial", "clinical", "repurpos", "pipeline"]):
            from src.tools.clinical_tool import find_repurposing_opportunities, query_clinical_trials
            if "pembrolizumab" in q:
                responses.append(find_repurposing_opportunities._run(molecule="Pembrolizumab"))
            else:
                responses.append(query_clinical_trials._run(indication="Oncology"))
            agents_used.append("Clinical")
        
        # Patient voice queries
        if any(w in q for w in ["patient complain", "patient voice", "patient feedback", "injectable"]):
            from src.tools.social_tool import analyze_patient_complaints
            responses.append(analyze_patient_complaints._run(therapy_area="Diabetes"))
            agents_used.append("Patient")
        
        # Competitor/War game queries
        if any(w in q for w in ["competitor", "war game", "simulate launch", "competitive threat"]):
            from src.tools.competitor_tool import war_game_scenario
            responses.append(war_game_scenario._run(molecule="Rivaroxaban", proposed_strategy="Launch generic in 2025"))
            agents_used.append("Competitor")
        
        # If we have tool responses, return them
        if responses:
            return "\n\n---\n\n".join(responses), agents_used
        
        # Try web search for current/news queries
        if any(w in q for w in ["latest", "recent", "news", "current", "2024", "2025", "today", "update", "fda"]):
            web_result = search_web(query)
            if web_result:
                return web_result, ["Web Search"]
        
        # Otherwise, use LLM with optional web context
        return ask_llm(query)
            
    except Exception as e:
        # Return user-friendly error message
        return f"⚠️ **Something went wrong**\n\nI encountered an issue processing your request. Please try:\n- Rephrasing your question\n- Being more specific about the molecule or therapy area\n- Checking if the data exists in our system\n\n*Technical details: {str(e)[:100]}*", ["System"]


def ask_llm(query: str) -> tuple:
    """Use Groq LLM to answer general pharmaceutical questions, with web search and conversation context."""
    import os
    from groq import Groq
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Check rate limit
    try:
        from src.services.rate_limiter import RateLimiter
        user_id = st.session_state.user["id"] if st.session_state.user else None
        allowed, current, limit = RateLimiter.check_limit("groq", user_id)
        
        if not allowed:
            return f"⚠️ **Rate limit reached** ({current}/{limit} calls today)\n\nYour daily API quota has been reached. Please try again tomorrow or contact an administrator for increased limits.", []
    except:
        pass
    
    try:
        web_context = search_web(query)
        
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        system_prompt = """You are a pharmaceutical intelligence assistant. You provide accurate, 
helpful information about:
- Medications, drugs, and their uses
- Dosages and administration
- Side effects and contraindications
- Drug interactions
- General pharmaceutical knowledge
- Medical conditions and treatments

Always include appropriate disclaimers about consulting healthcare professionals for medical advice.
Be concise but comprehensive. Format your response with clear headings and bullet points when appropriate.
If the user refers to previous context (like "it", "that drug", "the molecule"), use the conversation history to understand what they're referring to."""

        # Build messages with conversation context
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent conversation history for context (last 6 messages)
        if st.session_state.messages:
            recent_history = st.session_state.messages[-6:]
            for msg in recent_history:
                role = "user" if msg["role"] == "user" else "assistant"
                # Truncate long messages for context
                content = msg["content"][:1000] + "..." if len(msg["content"]) > 1000 else msg["content"]
                messages.append({"role": role, "content": content})
        
        # Build current user message
        user_message = query
        if web_context:
            user_message = f"""Question: {query}

Here is some relevant information from the web:
{web_context}

Please provide a comprehensive answer based on this information and your knowledge."""
            agents = ["Web Search", "AI Assistant"]
        else:
            agents = ["AI Assistant"]
        
        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=messages,
            temperature=0.3,
            max_tokens=2048
        )
        
        # Record usage
        try:
            from src.services.rate_limiter import RateLimiter
            user_id = st.session_state.user["id"] if st.session_state.user else None
            RateLimiter.record_usage("groq", user_id)
        except:
            pass
        
        answer = response.choices[0].message.content
        return answer, agents
        
    except Exception as e:
        error_msg = str(e)
        if "rate_limit" in error_msg.lower():
            return "⚠️ **API Rate Limit**\n\nThe AI service is temporarily rate-limited. Please wait a moment and try again.", []
        elif "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
            return "⚠️ **Configuration Error**\n\nThe AI service is not properly configured. Please contact an administrator.", []
        else:
            return f"⚠️ **Service Unavailable**\n\nI couldn't connect to the AI service. Please try again in a moment.\n\n*Error: {error_msg[:100]}*", []


def export_report(format_type: str):
    """Export last response as PDF or Excel."""
    if not st.session_state.last_response:
        return None
    
    try:
        if format_type == "PDF":
            from src.services.report_generator import generate_pdf_report
            path = generate_pdf_report(
                title="Pharma Strategy Analysis",
                query=st.session_state.last_query,
                content=st.session_state.last_response,
                metadata={
                    "agents_used": st.session_state.last_agents,
                    "user": st.session_state.user.get("username", "anonymous") if st.session_state.user else "anonymous"
                }
            )
            return path if not path.startswith("Error") else None
        else:
            from src.services.report_generator import generate_excel_report
            findings = [
                line.strip()[2:] for line in st.session_state.last_response.split("\n")
                if line.strip().startswith("- ") or line.strip().startswith("• ")
            ]
            path = generate_excel_report(
                title="Pharma Strategy Analysis",
                query=st.session_state.last_query,
                data={"findings": findings[:20], "recommendations": []},
                metadata={
                    "agents_used": st.session_state.last_agents,
                    "user": st.session_state.user.get("username", "anonymous") if st.session_state.user else "anonymous"
                }
            )
            return path if not path.startswith("Error") else None
    except Exception as e:
        st.error(f"Export failed: {e}")
        return None


def process_message(query: str):
    """Process a user message."""
    import time
    start_time = time.time()
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Save to database if logged in
    if st.session_state.logged_in and st.session_state.user:
        try:
            from src.services.conversation import ConversationService
            user_id = st.session_state.user["id"]
            
            # Create new conversation if needed
            if not st.session_state.conversation_id:
                st.session_state.conversation_id = ConversationService.create_conversation(user_id)
            
            # Save message
            ConversationService.add_message(st.session_state.conversation_id, "user", query)
        except Exception:
            pass
    
    # Check if user is asking to export
    q_lower = query.lower()
    if any(w in q_lower for w in ["export", "download", "generate report", "create pdf", "create excel", "save"]):
        if "pdf" in q_lower:
            path = export_report("PDF")
            if path:
                response = f"✅ **PDF Report Generated**\n\nSaved to: `{path}`"
            else:
                response = "❌ No analysis available to export. Ask a question first."
        elif "excel" in q_lower:
            path = export_report("Excel")
            if path:
                response = f"✅ **Excel Report Generated**\n\nSaved to: `{path}`"
            else:
                response = "❌ No analysis available to export. Ask a question first."
        else:
            response = "📄 **Export Options:**\n\n- Say **'export as PDF'** to generate a PDF report\n- Say **'export as Excel'** for a spreadsheet"
        
        st.session_state.messages.append({"role": "assistant", "content": response, "agents": []})
        return
    
    # Run the query
    success = True
    error_msg = None
    try:
        response, agents_used = run_demo_query(query)
    except Exception as e:
        success = False
        error_msg = str(e)
        response = f"⚠️ An error occurred: {str(e)}"
        agents_used = ["System"]
    
    # Calculate response time
    response_time_ms = int((time.time() - start_time) * 1000)
    
    # Track query for analytics
    try:
        from src.services.query_tracker import QueryTracker
        user_id = st.session_state.user["id"] if st.session_state.user else None
        QueryTracker.log_query(
            query_text=query,
            agents_used=agents_used,
            user_id=user_id,
            response_time_ms=response_time_ms,
            success=success,
            error_message=error_msg
        )
    except Exception:
        pass  # Don't fail if tracking fails
    
    # Store response for potential export
    st.session_state.last_response = response
    st.session_state.last_agents = agents_used
    st.session_state.last_query = query
    
    # Add assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "agents": agents_used
    })
    
    # Save to database
    if st.session_state.logged_in and st.session_state.conversation_id:
        try:
            from src.services.conversation import ConversationService
            ConversationService.add_message(st.session_state.conversation_id, "assistant", response, agents_used)
        except Exception:
            pass


def chat_interface():
    """Main chat interface."""
    # Display message history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("agents"):
                tags = " ".join([f'<span class="agent-tag">{a}</span>' for a in msg["agents"]])
                st.markdown(f"**Agents:** {tags}", unsafe_allow_html=True)
    
    # Handle pending example query
    if "pending_query" in st.session_state:
        query = st.session_state.pending_query
        del st.session_state.pending_query
        process_message(query)
        st.rerun()
    
    # Chat input
    if prompt := st.chat_input("Ask about pharmaceutical strategy, patents, trials, markets..."):
        process_message(prompt)
        st.rerun()


def export_buttons():
    """Export controls at bottom."""
    if st.session_state.last_response:
        st.markdown("---")
        cols = st.columns([3, 1, 1])
        with cols[0]:
            st.caption("💡 *Say 'export as PDF' or 'export as Excel' to save the analysis*")
        with cols[1]:
            if st.button("📥 PDF", use_container_width=True):
                path = export_report("PDF")
                if path:
                    st.success(f"Saved: {Path(path).name}")
        with cols[2]:
            if st.button("📊 Excel", use_container_width=True):
                path = export_report("Excel")
                if path:
                    st.success(f"Saved: {Path(path).name}")


def main():
    """Main entry point."""
    init_session()
    
    # Check if logged in
    if not st.session_state.logged_in:
        login_page()
        return
    
    # Main app
    sidebar()
    header()
    
    # Status bar with user info
    user = st.session_state.user
    status = f"🟢 {user['username']} ({user['role']}) — 9 Agents — Groq Llama 3.3 70B"
    st.markdown(f'<div class="status-bar">{status}</div>', unsafe_allow_html=True)
    
    chat_interface()
    export_buttons()
    
    # Footer
    st.markdown(
        f'<div class="footer">Pharma Agentic AI • {datetime.now().strftime("%Y")}</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
