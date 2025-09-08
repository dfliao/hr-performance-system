# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**HR Performance Management System** - An event-driven performance management system that integrates with Synology infrastructure (LDAP, Redmine, Chat, Drive, n8n automation).

## Architecture

### Backend (FastAPI + Python)
- **API Layer**: FastAPI with automatic OpenAPI documentation
- **Database**: MariaDB with SQLModel ORM
- **Authentication**: LDAP integration with JWT tokens
- **File Storage**: Synology Drive integration
- **External APIs**: Redmine, n8n webhooks

### Frontend (Vue.js 3 + TypeScript)
- **Framework**: Vue 3 with Composition API
- **UI Library**: Element Plus for enterprise UI components
- **State Management**: Pinia for centralized state
- **Build Tool**: Vite for fast development

### Database Schema
- **users**: LDAP-synced user data
- **departments**: Organizational hierarchy
- **events**: Performance events with scoring
- **rules**: Configurable scoring rules
- **scores**: Calculated performance scores
- **audit_logs**: Complete operation tracking

## Common Commands

### Development
```bash
# Backend development
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend development
cd frontend
npm run dev

# Database migrations
cd backend
alembic upgrade head

# Run tests
cd backend
pytest
cd ../frontend
npm run test
```

### Docker Deployment (Synology)
```bash
# Build and deploy
docker-compose up -d

# View logs
docker-compose logs -f

# Restart services
docker-compose restart
```

### Database Operations
```bash
# Connect to MariaDB
docker-compose exec db mysql -u hr_user -p hr_performance

# Backup database
docker-compose exec db mysqldump -u hr_user -p hr_performance > backup.sql

# Restore database
docker-compose exec -T db mysql -u hr_user -p hr_performance < backup.sql
```

## Key Features

### MVP Phase 1
1. **Event Management**: Create, edit, approve performance events
2. **Scoring Engine**: Automated calculation based on configurable rules
3. **Reports**: Personal performance cards and department summaries
4. **Authentication**: LDAP integration with role-based permissions
5. **File Handling**: Evidence file upload to Synology Drive

### Phase 2 Enhancements
1. **Batch Import**: CSV/Excel upload for bulk events
2. **Advanced Reports**: Trends, analytics, company overview
3. **Integration**: Full Redmine, n8n, Chat integration
4. **Workflow**: Multi-level approval processes

## File Organization

```
backend/
├── app/
│   ├── api/          # API routes and endpoints
│   ├── core/         # Configuration and security
│   ├── models/       # Database models
│   ├── services/     # Business logic
│   └── utils/        # Utility functions
├── alembic/          # Database migrations
└── tests/            # Backend tests

frontend/
├── src/
│   ├── components/   # Vue components
│   ├── views/        # Page components
│   ├── stores/       # Pinia stores
│   ├── services/     # API services
│   └── utils/        # Frontend utilities
├── public/           # Static assets
└── tests/            # Frontend tests

docker/               # Docker configurations
docs/                 # Documentation
scripts/              # Deployment and utility scripts
```

## Integration Points

### Synology LDAP
- Authentication backend
- User and department synchronization
- Role-based access control

### Redmine Integration
- Automatic event creation from task completion
- Project mapping to performance events
- Due date monitoring for penalty events

### Synology Drive
- Evidence file storage
- Secure file access with signed URLs
- Automated cleanup policies

### n8n Automation
- External data import webhooks
- Automated report generation
- Integration with third-party systems

## Security & Compliance

### Authentication
- LDAP/Active Directory integration
- JWT token-based API authentication
- Role-based access control (Admin, Manager, Employee, Auditor)

### Data Security
- Row-level security for data access
- Audit logging for all operations
- File access through signed URLs only

### Compliance
- Complete audit trail for all changes
- Data retention policies
- Export capabilities for compliance reporting

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
pytest tests/test_api.py::test_create_event -v
```

### Frontend Tests
```bash
cd frontend
npm run test:unit
npm run test:e2e
```

## Deployment Notes

### Synology Container Manager
- Use `docker-compose.yml` for deployment
- Configure reverse proxy for HTTPS
- Set up volume mounts for persistent data

### Environment Variables
```bash
# Database
DATABASE_URL=mysql://hr_user:password@db:3306/hr_performance

# LDAP
LDAP_SERVER=ldap://synology-ldap:389
LDAP_BASE_DN=dc=company,dc=com

# File Storage
SYNOLOGY_DRIVE_PATH=/volume1/hr-evidence
SYNOLOGY_DRIVE_URL=https://drive.company.com

# External APIs
REDMINE_URL=https://redmine.company.com
REDMINE_API_KEY=your_api_key
```

## Performance Considerations

### Database Optimization
- Indexes on frequently queried columns (user_id, department_id, occurred_at)
- Separate scores table for reporting performance
- Partitioning by date for large datasets

### Caching Strategy
- Redis for session and API response caching
- File metadata caching for Synology Drive
- Computed scores caching for reports

### Monitoring
- Application logs through Docker logging
- Performance monitoring for API endpoints
- Database performance tracking

## Troubleshooting

### Common Issues
1. **LDAP Connection**: Check network connectivity and credentials
2. **File Upload**: Verify Synology Drive permissions and paths
3. **Database Migration**: Ensure proper backup before schema changes
4. **Docker Issues**: Check container logs and resource limits

### Debug Commands
```bash
# Check API health
curl http://localhost:8000/health

# View application logs
docker-compose logs backend

# Connect to database
docker-compose exec db mysql -u hr_user -p
```