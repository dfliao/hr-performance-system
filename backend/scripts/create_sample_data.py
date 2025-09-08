#!/usr/bin/env python3
"""
Create sample data for development and testing
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from typing import List

# Add parent directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from sqlmodel import Session, create_engine, select
from passlib.context import CryptContext

from app.core.config import settings
from app.models import (
    User, Department, RulePack, Rule, Event, EventStatus, EventSource,
    Project, Period, PeriodType
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_sample_departments(db: Session) -> List[Department]:
    """Create sample departments"""
    departments_data = [
        {"name": "技術部", "code": "TECH", "description": "負責技術開發與維護"},
        {"name": "業務部", "code": "SALES", "description": "負責業務拓展與客戶關係"},
        {"name": "行銷部", "code": "MARKETING", "description": "負責市場推廣與品牌建立"},
        {"name": "人資部", "code": "HR", "description": "負責人力資源管理"},
        {"name": "財務部", "code": "FINANCE", "description": "負責財務管理與會計"},
        {"name": "營運部", "code": "OPERATIONS", "description": "負責日常營運與流程優化"},
    ]
    
    departments = []
    for dept_data in departments_data:
        # Check if department already exists
        existing = db.exec(select(Department).where(Department.code == dept_data["code"])).first()
        if existing:
            departments.append(existing)
            continue
            
        department = Department(
            name=dept_data["name"],
            code=dept_data["code"],
            description=dept_data["description"],
            is_active=True
        )
        db.add(department)
        departments.append(department)
    
    db.commit()
    
    for dept in departments:
        db.refresh(dept)
    
    return departments

def create_sample_users(db: Session, departments: List[Department]) -> List[User]:
    """Create sample users"""
    users_data = [
        # Admin users
        {
            "username": "admin",
            "name": "系統管理員",
            "email": "admin@company.com",
            "employee_id": "A001",
            "role": "admin",
            "department_id": departments[3].id,  # HR
            "password": "admin123"
        },
        {
            "username": "auditor",
            "name": "稽核員",
            "email": "auditor@company.com", 
            "employee_id": "A002",
            "role": "auditor",
            "department_id": departments[3].id,  # HR
            "password": "audit123"
        },
        
        # Managers
        {
            "username": "tech_manager",
            "name": "李技術",
            "email": "tech.manager@company.com",
            "employee_id": "M001",
            "role": "manager",
            "department_id": departments[0].id,  # Tech
            "password": "manager123"
        },
        {
            "username": "sales_manager",
            "name": "王業務",
            "email": "sales.manager@company.com",
            "employee_id": "M002", 
            "role": "manager",
            "department_id": departments[1].id,  # Sales
            "password": "manager123"
        },
        {
            "username": "marketing_manager",
            "name": "陳行銷",
            "email": "marketing.manager@company.com",
            "employee_id": "M003",
            "role": "manager", 
            "department_id": departments[2].id,  # Marketing
            "password": "manager123"
        },
        
        # Employees
        {
            "username": "john_dev",
            "name": "張開發",
            "email": "john.dev@company.com",
            "employee_id": "E001",
            "role": "employee",
            "department_id": departments[0].id,  # Tech
            "password": "employee123"
        },
        {
            "username": "mary_dev",
            "name": "林程式",
            "email": "mary.dev@company.com", 
            "employee_id": "E002",
            "role": "employee",
            "department_id": departments[0].id,  # Tech
            "password": "employee123"
        },
        {
            "username": "peter_sales",
            "name": "黃業務",
            "email": "peter.sales@company.com",
            "employee_id": "E003",
            "role": "employee",
            "department_id": departments[1].id,  # Sales
            "password": "employee123"
        },
        {
            "username": "lisa_marketing", 
            "name": "周行銷",
            "email": "lisa.marketing@company.com",
            "employee_id": "E004",
            "role": "employee",
            "department_id": departments[2].id,  # Marketing
            "password": "employee123"
        },
        {
            "username": "david_ops",
            "name": "吳營運",
            "email": "david.ops@company.com",
            "employee_id": "E005", 
            "role": "employee",
            "department_id": departments[5].id,  # Operations
            "password": "employee123"
        },
    ]
    
    users = []
    for user_data in users_data:
        # Check if user already exists
        existing = db.exec(select(User).where(User.username == user_data["username"])).first()
        if existing:
            users.append(existing)
            continue
            
        user = User(
            username=user_data["username"],
            name=user_data["name"],
            email=user_data["email"],
            employee_id=user_data["employee_id"],
            role=user_data["role"],
            department_id=user_data["department_id"],
            hashed_password=hash_password(user_data["password"]),
            is_active=True,
            last_login=datetime.utcnow()
        )
        db.add(user)
        users.append(user)
    
    db.commit()
    
    for user in users:
        db.refresh(user)
        
    return users

def create_sample_projects(db: Session) -> List[Project]:
    """Create sample projects"""
    projects_data = [
        {
            "name": "客戶管理系統",
            "code": "CRM2024",
            "description": "開發新一代客戶關係管理系統",
            "status": "active",
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 12, 31)
        },
        {
            "name": "市場推廣活動",
            "code": "MKT2024Q1", 
            "description": "第一季度市場推廣活動",
            "status": "completed",
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 3, 31)
        },
        {
            "name": "內部流程優化",
            "code": "OPT2024",
            "description": "優化內部作業流程提升效率",
            "status": "active",
            "start_date": date(2024, 2, 1),
            "end_date": date(2024, 6, 30)
        }
    ]
    
    projects = []
    for proj_data in projects_data:
        # Check if project already exists
        existing = db.exec(select(Project).where(Project.code == proj_data["code"])).first()
        if existing:
            projects.append(existing)
            continue
            
        project = Project(**proj_data)
        db.add(project)
        projects.append(project)
    
    db.commit()
    
    for project in projects:
        db.refresh(project)
        
    return projects

def create_sample_rule_pack_and_rules(db: Session) -> tuple[RulePack, List[Rule]]:
    """Create sample rule pack and rules"""
    
    # Check if rule pack already exists
    existing_pack = db.exec(select(RulePack).where(RulePack.name == "標準績效規則包 v1.0")).first()
    if existing_pack:
        existing_rules = db.exec(select(Rule).where(Rule.rule_pack_id == existing_pack.id)).all()
        return existing_pack, list(existing_rules)
    
    # Create rule pack
    rule_pack = RulePack(
        name="標準績效規則包 v1.0",
        version="1.0",
        description="公司標準績效評估規則",
        status="active",
        scope="company",
        effective_from=date(2024, 1, 1)
    )
    db.add(rule_pack)
    db.commit()
    db.refresh(rule_pack)
    
    # Rules data
    rules_data = [
        # Positive rules
        {
            "name": "優秀表現",
            "code": "EXCELLENT_PERF",
            "description": "工作表現優異，超越期望",
            "category": "performance",
            "base_score": 15,
            "weight": 1.0,
            "caps": 50,
            "evidence_required": True
        },
        {
            "name": "創新提案",
            "code": "INNOVATION",
            "description": "提出創新想法或改善建議",
            "category": "innovation",
            "base_score": 10,
            "weight": 1.2,
            "caps": 30,
            "evidence_required": True
        },
        {
            "name": "協助他人",
            "code": "HELP_OTHERS",
            "description": "主動協助同事完成工作",
            "category": "teamwork",
            "base_score": 5,
            "weight": 1.0,
            "caps": 20,
            "evidence_required": False
        },
        {
            "name": "準時完成",
            "code": "ON_TIME",
            "description": "按時完成指派任務",
            "category": "reliability",
            "base_score": 3,
            "weight": 1.0,
            "caps": 15,
            "evidence_required": False
        },
        {
            "name": "客戶好評",
            "code": "CUSTOMER_PRAISE",
            "description": "獲得客戶正面回饋",
            "category": "customer",
            "base_score": 12,
            "weight": 1.1,
            "caps": 40,
            "evidence_required": True
        },
        {
            "name": "技能提升",
            "code": "SKILL_IMPROVE",
            "description": "學習新技能或獲得認證",
            "category": "development",
            "base_score": 8,
            "weight": 1.0,
            "caps": 25,
            "evidence_required": True
        },
        
        # Negative rules  
        {
            "name": "遲到早退",
            "code": "LATE_LEAVE",
            "description": "上班遲到或提早離開",
            "category": "attendance",
            "base_score": -3,
            "weight": 1.0,
            "caps": 15,
            "evidence_required": False
        },
        {
            "name": "任務延遲",
            "code": "TASK_DELAY", 
            "description": "未能按時完成指派任務",
            "category": "reliability",
            "base_score": -5,
            "weight": 1.0,
            "caps": 20,
            "evidence_required": True
        },
        {
            "name": "品質問題",
            "code": "QUALITY_ISSUE",
            "description": "工作產出品質不佳需要返工",
            "category": "quality",
            "base_score": -8,
            "weight": 1.2,
            "caps": 25,
            "evidence_required": True
        },
        {
            "name": "客戶投訴",
            "code": "CUSTOMER_COMPLAINT",
            "description": "收到客戶負面回饋或投訴",
            "category": "customer",
            "base_score": -12,
            "weight": 1.3,
            "caps": 40,
            "evidence_required": True
        }
    ]
    
    rules = []
    for rule_data in rules_data:
        rule = Rule(
            rule_pack_id=rule_pack.id,
            **rule_data,
            active=True
        )
        db.add(rule)
        rules.append(rule)
    
    db.commit()
    
    for rule in rules:
        db.refresh(rule)
        
    return rule_pack, rules

def create_sample_events(db: Session, users: List[User], rules: List[Rule], projects: List[Project]) -> List[Event]:
    """Create sample events"""
    
    # Check if events already exist
    existing_count = db.exec(select(Event)).all()
    if len(existing_count) > 0:
        print(f"Found {len(existing_count)} existing events, skipping event creation")
        return existing_count
    
    events = []
    
    # Get current date and create events for the past 3 months
    today = date.today()
    start_date = today - timedelta(days=90)
    
    # Sample events data
    events_data = [
        # Positive events
        {
            "user": users[5],  # John Dev
            "rule": rules[0],  # Excellent Performance
            "title": "優化數據庫查詢性能",
            "description": "重構了關鍵查詢語句，將系統回應時間提升了 60%",
            "occurred_at": start_date + timedelta(days=5),
            "project": projects[0],
            "status": EventStatus.APPROVED
        },
        {
            "user": users[6],  # Mary Dev  
            "rule": rules[1],  # Innovation
            "title": "提出自動化測試框架",
            "description": "設計並實作自動化測試框架，大幅提升開發效率",
            "occurred_at": start_date + timedelta(days=12),
            "project": projects[0],
            "status": EventStatus.APPROVED
        },
        {
            "user": users[7],  # Peter Sales
            "rule": rules[4],  # Customer Praise
            "title": "獲得大客戶續約",
            "description": "成功說服重要客戶續約三年合約，業績表現優異",
            "occurred_at": start_date + timedelta(days=18),
            "status": EventStatus.APPROVED
        },
        {
            "user": users[8],  # Lisa Marketing
            "rule": rules[1],  # Innovation
            "title": "創新行銷策略",
            "description": "提出社群媒體整合行銷策略，獲得管理層採納",
            "occurred_at": start_date + timedelta(days=25),
            "project": projects[1],
            "status": EventStatus.APPROVED
        },
        {
            "user": users[9],  # David Ops
            "rule": rules[2],  # Help Others
            "title": "協助技術部解決系統問題",
            "description": "主動協助技術部解決服務器問題，展現團隊合作精神",
            "occurred_at": start_date + timedelta(days=30),
            "status": EventStatus.APPROVED
        },
        
        # More positive events
        {
            "user": users[5],  # John Dev
            "rule": rules[5],  # Skill Improve
            "title": "完成 AWS 認證",
            "description": "取得 AWS Solutions Architect 專業認證",
            "occurred_at": start_date + timedelta(days=35),
            "status": EventStatus.APPROVED
        },
        {
            "user": users[7],  # Peter Sales
            "rule": rules[3],  # On Time
            "title": "提前完成季度目標",
            "description": "提前兩週完成第一季度銷售目標",
            "occurred_at": start_date + timedelta(days=42),
            "status": EventStatus.APPROVED
        },
        
        # Some negative events
        {
            "user": users[6],  # Mary Dev
            "rule": rules[7],  # Task Delay
            "title": "專案進度延遲",
            "description": "因技術困難導致功能開發延遲一週",
            "occurred_at": start_date + timedelta(days=48),
            "project": projects[0],
            "status": EventStatus.APPROVED
        },
        {
            "user": users[9],  # David Ops
            "rule": rules[6],  # Late Leave
            "title": "上班遲到",
            "description": "本週累計遲到 3 次",
            "occurred_at": start_date + timedelta(days=55),
            "status": EventStatus.APPROVED
        },
        
        # Pending events (for demonstration)
        {
            "user": users[5],  # John Dev
            "rule": rules[0],  # Excellent Performance
            "title": "重構核心模組",
            "description": "重新設計核心業務模組，提升系統穩定性",
            "occurred_at": today - timedelta(days=3),
            "project": projects[0],
            "status": EventStatus.PENDING
        },
        {
            "user": users[8],  # Lisa Marketing
            "rule": rules[4],  # Customer Praise
            "title": "活動獲得好評",
            "description": "籌辦的產品發表會獲得客戶一致好評",
            "occurred_at": today - timedelta(days=1),
            "project": projects[1],
            "status": EventStatus.PENDING
        }
    ]
    
    # Create events
    for event_data in events_data:
        occurred_date = event_data["occurred_at"]
        user = event_data["user"]
        rule = event_data["rule"]
        
        event = Event(
            user_id=user.id,
            reporter_id=users[2].id,  # Tech manager as reporter
            department_id=user.department_id,
            project_id=event_data.get("project").id if event_data.get("project") else None,
            rule_id=rule.id,
            title=event_data["title"],
            description=event_data["description"],
            original_score=rule.base_score * rule.weight,
            final_score=rule.base_score * rule.weight,
            occurred_at=occurred_date,
            status=event_data["status"],
            evidence_urls=[],
            evidence_count=0,
            source=EventSource.MANUAL,
            period_year=occurred_date.year,
            period_month=occurred_date.month,
            period_quarter=(occurred_date.month - 1) // 3 + 1
        )
        
        # Set review info for approved events
        if event.status == EventStatus.APPROVED:
            event.reviewed_by = users[2].id  # Tech manager
            event.reviewed_at = datetime.combine(occurred_date, datetime.min.time()) + timedelta(days=1)
            event.review_notes = "已審核通過"
        
        db.add(event)
        events.append(event)
    
    db.commit()
    
    for event in events:
        db.refresh(event)
        
    return events

def create_sample_periods(db: Session) -> List[Period]:
    """Create sample periods for the current year"""
    
    current_year = date.today().year
    periods = []
    
    # Create monthly periods for current year
    for month in range(1, 13):
        existing = db.exec(select(Period).where(
            Period.type == PeriodType.MONTHLY,
            Period.year == current_year,
            Period.month == month
        )).first()
        
        if not existing:
            period = Period.generate_monthly_period(current_year, month)
            db.add(period)
            periods.append(period)
    
    db.commit()
    
    for period in periods:
        db.refresh(period)
        
    return periods

async def main():
    """Main function to create all sample data"""
    print("🎯 Creating sample data for HR Performance System...")
    
    # Create database engine
    engine = create_engine(str(settings.DATABASE_URL))
    
    with Session(engine) as db:
        try:
            print("📁 Creating sample departments...")
            departments = create_sample_departments(db)
            print(f"✅ Created {len(departments)} departments")
            
            print("👥 Creating sample users...")
            users = create_sample_users(db, departments)
            print(f"✅ Created {len(users)} users")
            
            print("📋 Creating sample projects...")
            projects = create_sample_projects(db)
            print(f"✅ Created {len(projects)} projects")
            
            print("📜 Creating sample rule pack and rules...")
            rule_pack, rules = create_sample_rule_pack_and_rules(db)
            print(f"✅ Created rule pack with {len(rules)} rules")
            
            print("📅 Creating sample periods...")
            periods = create_sample_periods(db)
            print(f"✅ Created {len(periods)} periods")
            
            print("🎪 Creating sample events...")
            events = create_sample_events(db, users, rules, projects)
            print(f"✅ Created {len(events)} events")
            
            print("\n🎉 Sample data creation completed successfully!")
            print("\n📊 Summary:")
            print(f"   • {len(departments)} departments")
            print(f"   • {len(users)} users")
            print(f"   • {len(projects)} projects")
            print(f"   • 1 rule pack with {len(rules)} rules")
            print(f"   • {len(periods)} periods")
            print(f"   • {len(events)} events")
            print("\n👤 Default admin credentials:")
            print("   Username: admin")
            print("   Password: admin123")
            
        except Exception as e:
            print(f"❌ Error creating sample data: {e}")
            db.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(main())