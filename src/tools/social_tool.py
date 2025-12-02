"""
Social Media Listening Tool
Queries mock social media data for patient voice analysis.
"""
import json
from typing import Optional
from crewai.tools import tool
from pathlib import Path


def _load_social_data() -> list:
    """Load social media mock data from JSON file."""
    data_path = Path(__file__).resolve().parent.parent.parent / "mock_data" / "social_media_posts.json"
    with open(data_path, "r") as f:
        return json.load(f)


@tool("Query Social Media Sentiment")
def query_social_media(molecule: Optional[str] = None, therapy_area: Optional[str] = None) -> str:
    """
    Query patient social media posts for sentiment and complaint analysis.
    
    Args:
        molecule: Drug name to search for patient feedback
        therapy_area: Therapeutic area (e.g., 'Diabetes', 'Respiratory')
    
    Returns:
        Patient posts with sentiment scores and complaint themes.
    """
    try:
        data = _load_social_data()
        results = []
        
        for post in data:
            if molecule and molecule.lower() not in post.get("molecule", "").lower():
                continue
            if therapy_area and therapy_area.lower() not in post.get("therapy_area", "").lower():
                continue
            results.append(post)
        
        if not results:
            return f"No social media data found for molecule='{molecule}', therapy_area='{therapy_area}'"
        
        output = []
        for post in results:
            sentiment = post["sentiment"]
            sentiment_label = "Positive" if sentiment > 0.3 else ("Negative" if sentiment < -0.3 else "Neutral")
            sentiment_emoji = "😊" if sentiment > 0.3 else ("😞" if sentiment < -0.3 else "😐")
            
            output.append(
                f"**{post['molecule']}** - {post['source']} ({post['date']})\n"
                f"  Sentiment: {sentiment_emoji} {sentiment_label} ({sentiment:.1f})\n"
                f"  Theme: {post.get('complaint_theme', 'N/A')}\n"
                f"  Quote: \"{post['post_text']}\"\n"
            )
        
        return "\n".join(output)
    
    except Exception as e:
        return f"Error querying social media: {str(e)}"


@tool("Analyze Patient Complaints")
def analyze_patient_complaints(therapy_area: str) -> str:
    """
    Analyze common patient complaints for a therapy area to identify innovation opportunities.
    
    Args:
        therapy_area: Therapeutic area to analyze (e.g., 'Diabetes', 'Respiratory')
    
    Returns:
        Summary of complaint themes and innovation opportunities.
    """
    try:
        data = _load_social_data()
        
        # Filter by therapy area
        posts = [p for p in data if therapy_area.lower() in p.get("therapy_area", "").lower()]
        
        if not posts:
            return f"No patient data found for therapy area: {therapy_area}"
        
        # Aggregate complaint themes
        themes = {}
        molecules = set()
        total_sentiment = 0
        
        for post in posts:
            theme = post.get("complaint_theme", "Other")
            themes[theme] = themes.get(theme, 0) + 1
            molecules.add(post["molecule"])
            total_sentiment += post["sentiment"]
        
        avg_sentiment = total_sentiment / len(posts)
        
        # Sort themes by frequency
        sorted_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)
        
        output = (
            f"**Patient Voice Analysis for {therapy_area}:**\n\n"
            f"**Posts Analyzed:** {len(posts)}\n"
            f"**Molecules Discussed:** {', '.join(molecules)}\n"
            f"**Average Sentiment:** {avg_sentiment:.2f} "
            f"({'Positive' if avg_sentiment > 0.3 else 'Negative' if avg_sentiment < -0.3 else 'Neutral'})\n\n"
            f"**Top Complaint Themes:**\n"
        )
        
        for theme, count in sorted_themes:
            pct = (count / len(posts)) * 100
            output += f"  - {theme}: {count} mentions ({pct:.0f}%)\n"
        
        # Innovation opportunities
        output += "\n**Innovation Opportunities:**\n"
        
        opportunity_map = {
            "Needle pain": "Develop oral or transdermal formulation",
            "Side effects": "Invest in better-tolerated next-gen compounds",
            "Storage issues": "Develop room-temperature stable formulation",
            "Cost": "Launch value brand or patient assistance program",
            "Ease of use": "Simplify device or reduce dosing frequency",
            "Device complexity": "Develop simpler delivery device",
            "Convenience": "Create more portable/discreet formulation"
        }
        
        for theme, _ in sorted_themes[:3]:
            if theme in opportunity_map:
                output += f"  ✅ {opportunity_map[theme]} (addresses '{theme}')\n"
        
        return output
    
    except Exception as e:
        return f"Error analyzing complaints: {str(e)}"


@tool("Get Patient Quotes")
def get_patient_quotes(molecule: str, limit: int = 5) -> str:
    """
    Get direct patient quotes about a specific drug for qualitative insights.
    
    Args:
        molecule: Drug name to get patient quotes for
        limit: Maximum number of quotes to return (default: 5)
    
    Returns:
        Direct patient quotes with sources and dates.
    """
    try:
        data = _load_social_data()
        
        quotes = [p for p in data if molecule.lower() in p.get("molecule", "").lower()]
        
        if not quotes:
            return f"No patient quotes found for: {molecule}"
        
        quotes = quotes[:limit]
        
        output = [f"**Patient Voices on {molecule}:**\n"]
        
        for q in quotes:
            sentiment = "👍" if q["sentiment"] > 0.3 else ("👎" if q["sentiment"] < -0.3 else "➖")
            output.append(
                f"{sentiment} \"{q['post_text']}\"\n"
                f"   — {q['source']}, {q['date']}\n"
            )
        
        return "\n".join(output)
    
    except Exception as e:
        return f"Error getting quotes: {str(e)}"
