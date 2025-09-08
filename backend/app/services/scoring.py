"""
Scoring engine - Calculate performance scores based on events and rules
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, date
from sqlmodel import Session, select, and_, func
from collections import defaultdict

from app.models import (
    Event, EventStatus, User, Rule, RulePack, Score, Period, PeriodType,
    ScoreCreate, ScoreUpdate
)
from app.services.audit import AuditService
from app.models import AuditAction, AuditEntityType


class ScoringEngine:
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)

    async def calculate_user_score(
        self,
        user_id: int,
        period_year: int,
        period_month: int,
        recalculate: bool = False
    ) -> Score:
        """Calculate performance score for a user in a specific period"""
        
        # Get or create period
        period = self._get_or_create_period(period_year, period_month)
        
        # Check if score already exists
        existing_score = self._get_existing_score(user_id, period.id)
        if existing_score and not recalculate and not existing_score.needs_recalculation:
            return existing_score
        
        # Get user
        user = self.db.get(User, user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        # Get approved events for the period
        events = self._get_events_for_period(user_id, period_year, period_month)
        
        # Get active rules
        active_rules = self._get_active_rules(user, period_year, period_month)
        
        # Calculate scores
        score_data = self._calculate_scores(events, active_rules, user, period)
        
        # Create or update score record
        if existing_score:
            updated_score = await self._update_score_record(existing_score, score_data)
        else:
            updated_score = await self._create_score_record(user_id, period.id, score_data)
        
        return updated_score

    async def calculate_department_scores(
        self,
        department_id: int,
        period_year: int,
        period_month: int,
        recalculate: bool = False
    ) -> List[Score]:
        """Calculate scores for all users in a department"""
        
        # Get all active users in department
        statement = select(User).where(
            and_(
                User.department_id == department_id,
                User.status == "active"
            )
        )
        users = self.db.exec(statement).all()
        
        scores = []
        for user in users:
            try:
                score = await self.calculate_user_score(
                    user.id, period_year, period_month, recalculate
                )
                scores.append(score)
            except Exception as e:
                print(f"Error calculating score for user {user.id}: {e}")
        
        # Calculate rankings
        await self._calculate_department_rankings(department_id, period_year, period_month)
        
        return scores

    async def calculate_company_scores(
        self,
        period_year: int,
        period_month: int,
        recalculate: bool = False
    ) -> List[Score]:
        """Calculate scores for all active users in the company"""
        
        # Get all active users
        statement = select(User).where(User.status == "active")
        users = self.db.exec(statement).all()
        
        scores = []
        for user in users:
            try:
                score = await self.calculate_user_score(
                    user.id, period_year, period_month, recalculate
                )
                scores.append(score)
            except Exception as e:
                print(f"Error calculating score for user {user.id}: {e}")
        
        # Calculate company-wide rankings
        await self._calculate_company_rankings(period_year, period_month)
        
        return scores

    def _get_or_create_period(self, year: int, month: int) -> Period:
        """Get existing period or create new one"""
        
        # Check if period exists
        statement = select(Period).where(
            and_(
                Period.type == PeriodType.MONTHLY,
                Period.year == year,
                Period.month == month
            )
        )
        period = self.db.exec(statement).first()
        
        if not period:
            # Create new period
            period = Period.generate_monthly_period(year, month)
            self.db.add(period)
            self.db.commit()
            self.db.refresh(period)
        
        return period

    def _get_existing_score(self, user_id: int, period_id: int) -> Optional[Score]:
        """Get existing score record"""
        
        statement = select(Score).where(
            and_(
                Score.user_id == user_id,
                Score.period_id == period_id
            )
        )
        return self.db.exec(statement).first()

    def _get_events_for_period(self, user_id: int, year: int, month: int) -> List[Event]:
        """Get approved events for user in specified period"""
        
        statement = select(Event).where(
            and_(
                Event.user_id == user_id,
                Event.period_year == year,
                Event.period_month == month,
                Event.status == EventStatus.APPROVED
            )
        )
        return self.db.exec(statement).all()

    def _get_active_rules(self, user: User, year: int, month: int) -> Dict[int, Rule]:
        """Get active rules applicable to the user"""
        
        # For now, get all active rules from active rule packs
        # TODO: Implement rule pack scope filtering (company/department/role)
        
        statement = select(Rule).join(RulePack).where(
            and_(
                Rule.active == True,
                RulePack.status == "active",
                RulePack.effective_from <= date(year, month, 1)
            )
        )
        
        rules = self.db.exec(statement).all()
        return {rule.id: rule for rule in rules}

    def _calculate_scores(
        self,
        events: List[Event],
        rules: Dict[int, Rule],
        user: User,
        period: Period
    ) -> Dict[str, Any]:
        """Calculate score components from events and rules"""
        
        total_score = 0.0
        positive_score = 0.0
        negative_score = 0.0
        adjusted_score = 0.0
        
        total_events = len(events)
        positive_events = 0
        negative_events = 0
        
        rule_breakdown = defaultdict(lambda: {
            "rule_name": "",
            "events": 0,
            "total_score": 0.0,
            "cap_applied": False
        })
        
        # Group events by rule for cap calculation
        events_by_rule = defaultdict(list)
        for event in events:
            events_by_rule[event.rule_id].append(event)
        
        # Calculate scores with caps
        for rule_id, rule_events in events_by_rule.items():
            rule = rules.get(rule_id)
            if not rule:
                continue
            
            rule_total = 0.0
            for event in rule_events:
                rule_total += event.final_score
                
                if event.final_score > 0:
                    positive_events += 1
                    positive_score += event.final_score
                else:
                    negative_events += 1
                    negative_score += event.final_score
                
                # Track adjustments
                if event.is_adjusted:
                    adjusted_score += (event.adjusted_score or 0) - event.original_score
            
            # Apply caps if defined
            original_rule_total = rule_total
            if rule.caps and abs(rule_total) > rule.caps:
                rule_total = rule.caps if rule_total > 0 else -rule.caps
                rule_breakdown[rule_id]["cap_applied"] = True
            
            total_score += rule_total
            
            rule_breakdown[rule_id].update({
                "rule_name": rule.name,
                "events": len(rule_events),
                "total_score": rule_total,
                "original_total": original_rule_total
            })
        
        return {
            "total_score": round(total_score, 2),
            "positive_score": round(positive_score, 2),
            "negative_score": round(negative_score, 2),
            "adjusted_score": round(adjusted_score, 2),
            "total_events": total_events,
            "positive_events": positive_events,
            "negative_events": negative_events,
            "pending_events": 0,  # Only counting approved events
            "rule_breakdown": dict(rule_breakdown),
            "events_computed_count": total_events,
            "computation_version": "1.0",
            "has_adjustments": adjusted_score != 0
        }

    async def _create_score_record(
        self,
        user_id: int,
        period_id: int,
        score_data: Dict[str, Any]
    ) -> Score:
        """Create new score record"""
        
        user = self.db.get(User, user_id)
        period = self.db.get(Period, period_id)
        
        score = Score(
            user_id=user_id,
            period_id=period_id,
            period_year=period.year,
            period_month=period.month,
            period_quarter=period.quarter,
            period_type=period.type,
            department_id=user.department_id,
            **score_data,
            computed_at=datetime.now(),
            is_locked=period.is_locked,
            needs_recalculation=False
        )
        
        self.db.add(score)
        self.db.commit()
        self.db.refresh(score)
        
        return score

    async def _update_score_record(
        self,
        score: Score,
        score_data: Dict[str, Any]
    ) -> Score:
        """Update existing score record"""
        
        # Update score fields
        for key, value in score_data.items():
            if hasattr(score, key):
                setattr(score, key, value)
        
        score.computed_at = datetime.now()
        score.needs_recalculation = False
        
        self.db.add(score)
        self.db.commit()
        self.db.refresh(score)
        
        return score

    async def _calculate_department_rankings(
        self,
        department_id: int,
        period_year: int,
        period_month: int
    ) -> None:
        """Calculate rankings within department"""
        
        # Get all scores for the department in this period
        statement = select(Score).where(
            and_(
                Score.department_id == department_id,
                Score.period_year == period_year,
                Score.period_month == period_month
            )
        ).order_by(Score.total_score.desc())
        
        scores = self.db.exec(statement).all()
        
        # Assign rankings and percentiles
        total_users = len(scores)
        for rank, score in enumerate(scores, 1):
            score.rank_department = rank
            score.percentile_department = ((total_users - rank + 1) / total_users) * 100
            self.db.add(score)
        
        self.db.commit()

    async def _calculate_company_rankings(
        self,
        period_year: int,
        period_month: int
    ) -> None:
        """Calculate company-wide rankings"""
        
        # Get all scores for this period
        statement = select(Score).where(
            and_(
                Score.period_year == period_year,
                Score.period_month == period_month
            )
        ).order_by(Score.total_score.desc())
        
        scores = self.db.exec(statement).all()
        
        # Assign company rankings and percentiles
        total_users = len(scores)
        for rank, score in enumerate(scores, 1):
            score.rank_company = rank
            score.percentile_company = ((total_users - rank + 1) / total_users) * 100
            self.db.add(score)
        
        self.db.commit()

    async def recalculate_period(
        self,
        period_year: int,
        period_month: int,
        department_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Recalculate all scores for a period"""
        
        base_query = select(User).where(User.status == "active")
        
        if department_id:
            base_query = base_query.where(User.department_id == department_id)
        
        users = self.db.exec(base_query).all()
        
        results = {
            "period": f"{period_year}-{period_month:02d}",
            "total_users": len(users),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        for user in users:
            try:
                await self.calculate_user_score(
                    user.id, period_year, period_month, recalculate=True
                )
                results["successful"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"User {user.id}: {str(e)}")
        
        # Recalculate rankings
        if department_id:
            await self._calculate_department_rankings(department_id, period_year, period_month)
        else:
            await self._calculate_company_rankings(period_year, period_month)
        
        return results