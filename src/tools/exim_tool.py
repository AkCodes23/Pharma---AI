"""
EXIM Trade Data Tool
Queries mock import/export data for supply chain analysis.
"""
import json
from crewai.tools import tool
from pathlib import Path


def _load_exim_data() -> list:
    """Load EXIM mock data from JSON file."""
    data_path = Path(__file__).resolve().parent.parent.parent / "mock_data" / "exim_trade_data.json"
    with open(data_path, "r") as f:
        return json.load(f)


@tool("Query EXIM Trade Data")
def query_exim_trade(molecule: str) -> str:
    """
    Query import/export trade data for a pharmaceutical molecule.
    
    Args:
        molecule: Name of the molecule/API to search for trade data.
    
    Returns:
        Trade data including import volumes, source countries, and pricing.
    """
    try:
        data = _load_exim_data()
        
        result = None
        for entry in data:
            if molecule.lower() in entry.get("molecule", "").lower():
                result = entry
                break
        
        if not result:
            return f"No EXIM trade data found for molecule: {molecule}"
        
        # Calculate total value
        total_value = result["total_import_volume_kg"] * result["average_price_per_kg"]
        
        output = (
            f"**EXIM Trade Data for {result['molecule']}:**\n\n"
            f"📦 **Import Volume:** {result['total_import_volume_kg']:,} kg\n"
            f"💰 **Average Price:** ${result['average_price_per_kg']:,.2f}/kg\n"
            f"💵 **Estimated Total Value:** ${total_value:,.0f}\n\n"
            f"🌍 **Major Source Countries:**\n"
        )
        
        for country in result["major_source_countries"]:
            output += f"  - {country}\n"
        
        # Add supply chain insights
        if result["average_price_per_kg"] > 10000:
            output += "\n⚠️ **High-value API** - Likely biologic or specialty drug"
        elif result["average_price_per_kg"] < 500:
            output += "\n✅ **Commodity API** - Multiple suppliers available"
        
        return output
    
    except Exception as e:
        return f"Error querying EXIM data: {str(e)}"


@tool("Analyze Supply Chain")
def analyze_supply_chain(molecule: str) -> str:
    """
    Analyze supply chain concentration and pricing for a molecule.
    
    Args:
        molecule: Name of the molecule to analyze.
    
    Returns:
        Supply chain risk assessment and sourcing recommendations.
    """
    try:
        data = _load_exim_data()
        
        result = None
        for entry in data:
            if molecule.lower() in entry.get("molecule", "").lower():
                result = entry
                break
        
        if not result:
            return f"No supply chain data found for: {molecule}"
        
        countries = result["major_source_countries"]
        price = result["average_price_per_kg"]
        volume = result["total_import_volume_kg"]
        
        # Assess concentration risk
        if len(countries) == 1:
            concentration_risk = "HIGH"
            risk_desc = "Single source country - significant supply risk"
        elif len(countries) == 2:
            concentration_risk = "MEDIUM"
            risk_desc = "Limited diversification - moderate supply risk"
        else:
            concentration_risk = "LOW"
            risk_desc = "Multiple source countries - diversified supply"
        
        # China dependency check
        china_dependent = "China" in countries
        
        output = (
            f"**Supply Chain Analysis for {result['molecule']}:**\n\n"
            f"**Concentration Risk:** {concentration_risk}\n"
            f"  {risk_desc}\n\n"
            f"**Source Countries:** {', '.join(countries)}\n"
        )
        
        if china_dependent:
            output += "⚠️ **China Dependency Alert:** Consider alternate sourcing\n"
        
        output += (
            f"\n**Pricing Analysis:**\n"
            f"  - Current Price: ${price:,.2f}/kg\n"
            f"  - Annual Import Value: ${price * volume:,.0f}\n"
        )
        
        # Recommendations
        output += "\n**Recommendations:**\n"
        if concentration_risk == "HIGH":
            output += "  - Qualify additional suppliers from alternate regions\n"
        if china_dependent:
            output += "  - Explore India or European API manufacturers\n"
        if price > 50000:
            output += "  - Consider backward integration for cost control\n"
        
        return output
    
    except Exception as e:
        return f"Error analyzing supply chain: {str(e)}"
