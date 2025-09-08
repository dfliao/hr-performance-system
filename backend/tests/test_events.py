"""
Test cases for event management API
"""

import pytest
from datetime import date, datetime
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models import Event, EventStatus, EventSource

class TestEventAPI:
    """Test event management endpoints"""
    
    def test_create_event(self, client: TestClient, auth_headers: dict, sample_user, sample_rule, helpers):
        """Test creating a new event"""
        event_data = {
            "user_id": sample_user.id,
            "rule_id": sample_rule.id,
            "title": "測試事件",
            "description": "這是一個測試事件",
            "occurred_at": "2024-01-15",
            "source": "manual"
        }
        
        response = client.post("/api/events", json=event_data, headers=auth_headers)
        
        helpers.assert_response_success(response)
        data = response.json()
        
        assert data["title"] == event_data["title"]
        assert data["description"] == event_data["description"]
        assert data["user_id"] == sample_user.id
        assert data["rule_id"] == sample_rule.id
        assert data["status"] == "pending"
    
    def test_get_event_list(self, client: TestClient, auth_headers: dict, helpers):
        """Test getting event list"""
        response = client.get("/api/events", headers=auth_headers)
        
        helpers.assert_response_success(response)
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
    
    def test_get_event_by_id(self, client: TestClient, auth_headers: dict, session: Session, 
                           sample_user, sample_rule, helpers):
        """Test getting specific event by ID"""
        # First create an event
        event = Event(
            user_id=sample_user.id,
            reporter_id=sample_user.id,
            department_id=sample_user.department_id,
            rule_id=sample_rule.id,
            title="測試事件",
            description="這是一個測試事件",
            original_score=10.0,
            final_score=10.0,
            occurred_at=datetime(2024, 1, 15),
            status=EventStatus.PENDING,
            evidence_urls=[],
            evidence_count=0,
            source=EventSource.MANUAL,
            period_year=2024,
            period_month=1,
            period_quarter=1
        )
        session.add(event)
        session.commit()
        session.refresh(event)
        
        # Test getting the event
        response = client.get(f"/api/events/{event.id}", headers=auth_headers)
        
        helpers.assert_response_success(response)
        data = response.json()
        
        assert data["id"] == event.id
        assert data["title"] == event.title
        assert data["status"] == "pending"
    
    def test_update_event(self, client: TestClient, auth_headers: dict, session: Session,
                         sample_user, sample_rule, helpers):
        """Test updating an event"""
        # First create an event
        event = Event(
            user_id=sample_user.id,
            reporter_id=sample_user.id,
            department_id=sample_user.department_id,
            rule_id=sample_rule.id,
            title="原始標題",
            description="原始描述",
            original_score=10.0,
            final_score=10.0,
            occurred_at=datetime(2024, 1, 15),
            status=EventStatus.DRAFT,  # Draft status allows editing
            evidence_urls=[],
            evidence_count=0,
            source=EventSource.MANUAL,
            period_year=2024,
            period_month=1,
            period_quarter=1
        )
        session.add(event)
        session.commit()
        session.refresh(event)
        
        # Update the event
        update_data = {
            "title": "更新的標題",
            "description": "更新的描述"
        }
        
        response = client.patch(f"/api/events/{event.id}", json=update_data, headers=auth_headers)
        
        helpers.assert_response_success(response)
        data = response.json()
        
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
    
    def test_approve_event(self, client: TestClient, admin_auth_headers: dict, session: Session,
                          sample_user, sample_rule, helpers):
        """Test approving an event (admin only)"""
        # First create a pending event
        event = Event(
            user_id=sample_user.id,
            reporter_id=sample_user.id,
            department_id=sample_user.department_id,
            rule_id=sample_rule.id,
            title="待審核事件",
            description="這個事件需要審核",
            original_score=10.0,
            final_score=10.0,
            occurred_at=datetime(2024, 1, 15),
            status=EventStatus.PENDING,
            evidence_urls=[],
            evidence_count=0,
            source=EventSource.MANUAL,
            period_year=2024,
            period_month=1,
            period_quarter=1
        )
        session.add(event)
        session.commit()
        session.refresh(event)
        
        # Approve the event
        approval_data = {
            "status": "approved",
            "review_notes": "看起來不錯，已核准"
        }
        
        response = client.post(f"/api/events/{event.id}/approve", 
                             json=approval_data, headers=admin_auth_headers)
        
        helpers.assert_response_success(response)
        data = response.json()
        
        assert data["status"] == "approved"
        assert data["review_notes"] == approval_data["review_notes"]
    
    def test_delete_event(self, client: TestClient, admin_auth_headers: dict, session: Session,
                         sample_user, sample_rule, helpers):
        """Test deleting an event (admin only)"""
        # First create an event
        event = Event(
            user_id=sample_user.id,
            reporter_id=sample_user.id,
            department_id=sample_user.department_id,
            rule_id=sample_rule.id,
            title="要刪除的事件",
            description="這個事件將被刪除",
            original_score=10.0,
            final_score=10.0,
            occurred_at=datetime(2024, 1, 15),
            status=EventStatus.DRAFT,
            evidence_urls=[],
            evidence_count=0,
            source=EventSource.MANUAL,
            period_year=2024,
            period_month=1,
            period_quarter=1
        )
        session.add(event)
        session.commit()
        session.refresh(event)
        
        # Delete the event
        response = client.delete(f"/api/events/{event.id}", headers=admin_auth_headers)
        
        assert response.status_code == 204
        
        # Verify event is deleted
        response = client.get(f"/api/events/{event.id}", headers=admin_auth_headers)
        assert response.status_code == 404
    
    def test_unauthorized_access(self, client: TestClient, helpers):
        """Test that unauthorized access is rejected"""
        response = client.get("/api/events")
        helpers.assert_response_error(response, 401)
    
    def test_create_event_validation(self, client: TestClient, auth_headers: dict, helpers):
        """Test event creation with invalid data"""
        # Missing required fields
        event_data = {
            "title": "測試事件"
            # Missing user_id, rule_id, etc.
        }
        
        response = client.post("/api/events", json=event_data, headers=auth_headers)
        helpers.assert_response_error(response, 422)
    
    def test_filter_events_by_status(self, client: TestClient, auth_headers: dict, helpers):
        """Test filtering events by status"""
        response = client.get("/api/events?status_filter=pending", headers=auth_headers)
        
        helpers.assert_response_success(response)
        data = response.json()
        
        assert "items" in data
        # All returned items should have pending status
        for item in data["items"]:
            assert item["status"] == "pending"
    
    def test_search_events(self, client: TestClient, auth_headers: dict, helpers):
        """Test searching events by title/description"""
        response = client.get("/api/events?search=測試", headers=auth_headers)
        
        helpers.assert_response_success(response)
        data = response.json()
        
        assert "items" in data