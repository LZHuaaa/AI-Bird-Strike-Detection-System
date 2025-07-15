from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from db import BirdAlert, DatabaseManager

class AlertResponse:
    def __init__(self, db_session: Session):
        self.db = db_session

    def respond_to_alert(
        self,
        alert_id: int,
        responder: str,
        action_taken: str,
        should_resolve: bool = False,
        ai_analysis: Optional[str] = None
    ) -> Optional[BirdAlert]:
        """
        Respond to a bird alert
        
        Parameters:
        - alert_id: ID of the alert to respond to
        - responder: Name/ID of the person responding
        - action_taken: Action taken in response (MONITOR, DELAY_TAKEOFF, EMERGENCY_PROTOCOL, etc.)
        - should_resolve: Whether to mark the alert as resolved
        - ai_analysis: Optional AI analysis of the situation
        
        Returns:
        - Updated BirdAlert object or None if alert not found
        """
        try:
            # Get the alert
            alert = self.db.query(BirdAlert).filter(BirdAlert.id == alert_id).first()
            
            if not alert:
                print(f"❌ Alert {alert_id} not found")
                return None
            
            current_time = datetime.utcnow()
            
            # Update alert acknowledgment
            if not alert.acknowledged:
                alert.acknowledged = True
                alert.acknowledged_by = responder
                alert.acknowledged_at = current_time
            
            # Update action taken
            alert.action_taken = action_taken
            
            # Update resolution status if requested
            if should_resolve and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = current_time
            
            # Add AI analysis if provided
            if ai_analysis:
                alert.ai_analysis = ai_analysis
            
            # Commit changes
            self.db.commit()
            print(f"✅ Alert {alert_id} updated successfully")
            
            return alert
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error updating alert {alert_id}: {str(e)}")
            return None

    def get_alert_status(self, alert_id: int) -> dict:
        """
        Get the current status of an alert
        
        Parameters:
        - alert_id: ID of the alert to check
        
        Returns:
        - Dictionary containing alert status information
        """
        try:
            alert = self.db.query(BirdAlert).filter(BirdAlert.id == alert_id).first()
            
            if not alert:
                return {"error": f"Alert {alert_id} not found"}
            
            return {
                "id": alert.id,
                "acknowledged": alert.acknowledged,
                "acknowledged_by": alert.acknowledged_by,
                "acknowledged_at": alert.acknowledged_at,
                "action_taken": alert.action_taken,
                "resolved": alert.resolved,
                "resolved_at": alert.resolved_at,
                "alert_level": alert.alert_level,
                "risk_score": alert.risk_score
            }
            
        except Exception as e:
            return {"error": f"Error getting alert status: {str(e)}"}

# Example usage:
def example_usage():
    """Example of how to use the AlertResponse class"""
    db_manager = DatabaseManager()
    
    # Create alert response handler
    alert_handler = AlertResponse(db_manager.session)
    
    # Respond to an alert
    updated_alert = alert_handler.respond_to_alert(
        alert_id=1,
        responder="John Smith",
        action_taken="DELAY_TAKEOFF",
        should_resolve=True,
        ai_analysis="High risk of bird strike due to flock movement pattern"
    )
    
    if updated_alert:
        print("Alert response recorded successfully")
        
        # Get updated status
        status = alert_handler.get_alert_status(1)
        print(f"Current alert status: {status}")
    
    # Always close the database connection
    db_manager.close()

if __name__ == "__main__":
    # This will run the example if the file is executed directly
    example_usage() 