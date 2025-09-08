"""
Audit logging service - Track all system operations
"""

from typing import Dict, Any, Optional
from datetime import datetime
from sqlmodel import Session

from app.models import AuditLog, AuditAction, AuditEntityType, User


class AuditService:
    def __init__(self, db: Session):
        self.db = db

    async def log_action(
        self,
        actor: User,
        action: AuditAction,
        entity_type: AuditEntityType,
        entity_id: Optional[int] = None,
        entity_name: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None,
        request_method: Optional[str] = None,
        request_path: Optional[str] = None,
        request_id: Optional[str] = None,
        session_id: Optional[str] = None,
        execution_time_ms: Optional[int] = None
    ) -> AuditLog:
        """Log an audit action"""
        
        # Calculate diff if both old and new values are provided
        diff = None
        if old_values and new_values:
            diff = {}
            all_keys = set(old_values.keys()) | set(new_values.keys())
            for key in all_keys:
                old_val = old_values.get(key)
                new_val = new_values.get(key)
                if old_val != new_val:
                    diff[key] = {
                        "old": old_val,
                        "new": new_val
                    }
        
        # Calculate risk score based on action and entity type
        risk_score = self._calculate_risk_score(action, entity_type, actor.role)
        
        # Determine if action is sensitive
        is_sensitive = action in [AuditAction.DELETE, AuditAction.EXPORT] or entity_type == AuditEntityType.USER
        
        # Determine if action requires review
        requires_review = (
            risk_score >= 60 or
            (action == AuditAction.DELETE and entity_type != AuditEntityType.EVENT) or
            (action == AuditAction.UPDATE and entity_type == AuditEntityType.RULE)
        )
        
        audit_log = AuditLog(
            actor_id=actor.id,
            actor_username=actor.username,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            old_values=old_values,
            new_values=new_values,
            diff=diff,
            description=description,
            metadata=metadata,
            success=success,
            error_message=error_message,
            request_method=request_method,
            request_path=request_path,
            request_id=request_id,
            session_id=session_id,
            execution_time_ms=execution_time_ms,
            risk_score=risk_score,
            is_sensitive=is_sensitive,
            requires_review=requires_review,
            timestamp=datetime.utcnow()
        )
        
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        
        return audit_log

    def _calculate_risk_score(self, action: AuditAction, entity_type: AuditEntityType, actor_role: str) -> int:
        """Calculate risk score for an action"""
        
        base_score = {
            AuditAction.CREATE: 10,
            AuditAction.READ: 0,
            AuditAction.UPDATE: 20,
            AuditAction.DELETE: 60,
            AuditAction.LOGIN: 5,
            AuditAction.LOGOUT: 0,
            AuditAction.APPROVE: 15,
            AuditAction.REJECT: 15,
            AuditAction.EXPORT: 40,
            AuditAction.IMPORT: 30,
            AuditAction.LOCK: 25,
            AuditAction.UNLOCK: 25,
            AuditAction.CALCULATE: 10
        }.get(action, 10)
        
        entity_multiplier = {
            AuditEntityType.USER: 1.5,
            AuditEntityType.DEPARTMENT: 1.3,
            AuditEntityType.RULE_PACK: 1.4,
            AuditEntityType.RULE: 1.2,
            AuditEntityType.EVENT: 1.0,
            AuditEntityType.SCORE: 1.1,
            AuditEntityType.PERIOD: 1.3,
            AuditEntityType.REPORT: 1.1,
            AuditEntityType.SYSTEM: 1.6
        }.get(entity_type, 1.0)
        
        role_modifier = {
            "admin": 0.8,  # Lower risk for admin actions
            "auditor": 0.9,
            "manager": 1.0,
            "employee": 1.2  # Higher risk for employee actions
        }.get(actor_role, 1.0)
        
        risk_score = int(base_score * entity_multiplier * role_modifier)
        return min(max(risk_score, 0), 100)  # Clamp between 0-100