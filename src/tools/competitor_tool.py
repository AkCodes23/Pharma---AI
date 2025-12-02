"""
Competitor Intelligence Tool
Queries mock competitor strategy data for war gaming analysis.
"""
import json
from crewai.tools import tool
from pathlib import Path


def _load_competitor_data() -> list:
    """Load competitor strategy mock data from JSON file."""
    data_path = Path(__file__).resolve().parent.parent.parent / "mock_data" / "competitor_strategies.json"
    with open(data_path, "r") as f:
        return json.load(f)


@tool("Query Competitor Intelligence")
def query_competitor_intel(molecule: str) -> str:
    """
    Query competitive intelligence for a specific molecule.
    
    Args:
        molecule: Molecule name to get competitor strategies for.
    
    Returns:
        Predicted competitor strategies, likelihood, and impact.
    """
    try:
        data = _load_competitor_data()
        
        results = [entry for entry in data if molecule.lower() in entry.get("molecule", "").lower()]
        
        if not results:
            return f"No competitor intelligence found for: {molecule}"
        
        output = [f"**Competitor Intelligence for {molecule}:**\n"]
        
        for intel in results:
            likelihood_emoji = "🔴" if intel["likelihood"] == "High" else ("🟡" if intel["likelihood"] == "Medium" else "🟢")
            
            output.append(
                f"**{intel['competitor']}**\n"
                f"  Strategy: {intel['predicted_strategy']}\n"
                f"  {likelihood_emoji} Likelihood: {intel['likelihood']}\n"
                f"  Impact: {intel['impact']}\n"
            )
        
        return "\n".join(output)
    
    except Exception as e:
        return f"Error querying competitor intel: {str(e)}"


@tool("War Game Scenario")
def war_game_scenario(molecule: str, proposed_strategy: str) -> str:
    """
    Simulate a war game scenario: predict competitor responses to your proposed strategy.
    
    Args:
        molecule: Molecule for which strategy is being proposed
        proposed_strategy: Your proposed strategic move (e.g., 'Launch generic in 2025', 'Price cut 30%')
    
    Returns:
        Predicted competitor counter-moves and risk assessment.
    """
    try:
        data = _load_competitor_data()
        
        results = [entry for entry in data if molecule.lower() in entry.get("molecule", "").lower()]
        
        if not results:
            return f"No competitor data available for war gaming: {molecule}"
        
        output = [
            f"**War Game Simulation: {molecule}**\n",
            f"**Your Proposed Strategy:** {proposed_strategy}\n",
            f"\n**Predicted Competitor Responses:**\n"
        ]
        
        risk_score = 0
        counter_moves = []
        
        for intel in results:
            likelihood = intel["likelihood"]
            
            # Assess risk based on likelihood
            if likelihood == "High":
                risk_score += 3
            elif likelihood == "Medium":
                risk_score += 2
            else:
                risk_score += 1
            
            # Generate counter-move prediction
            counter_move = _generate_counter_move(intel, proposed_strategy)
            counter_moves.append((intel["competitor"], counter_move, likelihood, intel["impact"]))
        
        for competitor, counter, likelihood, impact in counter_moves:
            output.append(
                f"**{competitor}:**\n"
                f"  Likely Counter: {counter}\n"
                f"  Probability: {likelihood} | Impact: {impact}\n"
            )
        
        # Overall risk assessment
        avg_risk = risk_score / len(results)
        risk_level = "HIGH" if avg_risk > 2.5 else ("MEDIUM" if avg_risk > 1.5 else "LOW")
        
        output.append(f"\n**Overall Risk Assessment: {risk_level}**\n")
        
        # Recommendations
        output.append("\n**Strategic Recommendations:**\n")
        if risk_level == "HIGH":
            output.append("  ⚠️ High competitive response expected - consider phased approach\n")
            output.append("  ⚠️ Build war chest for potential price competition\n")
            output.append("  ⚠️ Secure supply chain before announcement\n")
        elif risk_level == "MEDIUM":
            output.append("  ℹ️ Prepare for moderate competitive response\n")
            output.append("  ℹ️ Focus on differentiation beyond price\n")
        else:
            output.append("  ✅ Limited competitive response expected\n")
            output.append("  ✅ First-mover advantage possible\n")
        
        return "\n".join(output)
    
    except Exception as e:
        return f"Error running war game: {str(e)}"


def _generate_counter_move(intel: dict, proposed_strategy: str) -> str:
    """Generate a predicted counter-move based on intel and proposed strategy."""
    base_strategy = intel["predicted_strategy"]
    
    # Simple logic to create counter-move narrative
    if "price" in proposed_strategy.lower() or "discount" in proposed_strategy.lower():
        return f"Likely to match or undercut pricing. {base_strategy}"
    elif "launch" in proposed_strategy.lower() or "generic" in proposed_strategy.lower():
        return f"May accelerate own launch timeline. {base_strategy}"
    else:
        return base_strategy


@tool("Assess Competitive Threats")
def assess_competitive_threats(molecule: str) -> str:
    """
    Provide a threat assessment summary for a molecule.
    
    Args:
        molecule: Molecule to assess competitive threats for.
    
    Returns:
        Threat level summary with recommended counter-strategies.
    """
    try:
        data = _load_competitor_data()
        
        results = [entry for entry in data if molecule.lower() in entry.get("molecule", "").lower()]
        
        if not results:
            return f"No threat data available for: {molecule}"
        
        high_threats = [r for r in results if r["likelihood"] == "High"]
        medium_threats = [r for r in results if r["likelihood"] == "Medium"]
        
        overall_threat = "HIGH" if len(high_threats) >= 2 else ("MEDIUM" if len(high_threats) >= 1 else "LOW")
        
        output = (
            f"**Competitive Threat Assessment: {molecule}**\n\n"
            f"**Overall Threat Level: {overall_threat}**\n"
            f"  - High Probability Threats: {len(high_threats)}\n"
            f"  - Medium Probability Threats: {len(medium_threats)}\n\n"
        )
        
        if high_threats:
            output += "**Critical Threats:**\n"
            for threat in high_threats:
                output += f"  🔴 {threat['competitor']}: {threat['predicted_strategy']}\n"
        
        output += "\n**Recommended Counter-Strategies:**\n"
        
        counter_strategies = [
            "Build brand loyalty before generic entry",
            "Develop next-generation formulation",
            "Establish authorized generic program",
            "Secure key opinion leader endorsements",
            "Create patient switching barriers"
        ]
        
        for i, strategy in enumerate(counter_strategies[:3], 1):
            output += f"  {i}. {strategy}\n"
        
        return output
    
    except Exception as e:
        return f"Error assessing threats: {str(e)}"
