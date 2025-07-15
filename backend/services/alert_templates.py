"""
Predefined templates for alert responses
"""

from typing import Dict, Any

RESPONSE_TEMPLATES = {
    "MONITOR": {
        "action": "Area inspected, no threats detected",
        "notes": "Completed routine perimeter check",
        "status_update": {
            "alert_level": "LOW",
            "risk_score_adjustment": -10
        }
    },
    "DETERRENT": {
        "action": "Deployed deterrent measures",
        "notes": "Activated sonic and visual deterrents",
        "status_update": {
            "alert_level": "MEDIUM",
            "risk_score_adjustment": -20
        }
    },
    "SECURED": {
        "action": "Area secured",
        "notes": "Implemented standard operating procedures",
        "status_update": {
            "alert_level": "LOW",
            "risk_score_adjustment": -30
        }
    },
    "CLEAR": {
        "action": "All clear - no threats",
        "notes": "Situation resolved, no further action needed",
        "status_update": {
            "alert_level": "LOW",
            "risk_score_adjustment": -40
        }
    }
}

def get_response_template(template_key: str) -> Dict[str, Any]:
    """
    Get a response template by key
    """
    return RESPONSE_TEMPLATES.get(template_key, {})

def get_all_templates() -> Dict[str, Dict[str, Any]]:
    """
    Get all available response templates
    """
    return RESPONSE_TEMPLATES 