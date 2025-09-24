# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an ISMS (Information Security Management System) web application built for ISO/IEC 27001 compliance management. The application helps organizations manage security controls, risks, documentation, audits, and compliance workflows.

**Tech Stack:**
- Backend: Python with Flask
- Frontend: Flask templates (server-side rendering)
- Database: PostgreSQL with SQLAlchemy ORM
- Authentication: JWT or Flask sessions
- Deployment: Docker, Nginx, Gunicorn

## Development Commands

Since this is a new project, common Flask development commands will likely include:

```bash
# Development server
python app.py
# or
flask run

# Database migrations
flask db init
flask db migrate -m "description"
flask db upgrade

# Testing
python -m pytest
# or
pytest

# Linting
flake8 .
# or
python -m flake8

# Install dependencies
pip install -r requirements.txt
```

## Architecture and Code Organization

The application should follow Flask Blueprint architecture for modularity:

### Expected Module Structure
- **SOA Management**: Statement of Applicability with ISO 27001 Annex A controls
- **Risk Management**: Risk identification, assessment, and treatment
- **Document Management**: Version control for policies, procedures, instructions, records, and meeting minutes
- **Dashboard/KPIs**: Compliance metrics, maturity assessment, and system status indicators
- **Non-Conformity Management**: Issue tracking with root cause analysis and corrective action plans
- **Incident Management**: Security incident lifecycle management
- **Audit Management**: Internal audit planning, execution, and tracking
- **Task Management**: Periodic task scheduling and tracking
- **Training Management**: Security awareness and training records
- **Access Control**: Role-based permissions system

### Role-Based Access Control
The system implements five user roles:
- **System Administrator**: Full system access
- **Security Manager (CISO)**: All modules with approval rights
- **Internal Auditor**: Audit module + read access to others
- **Process Owner**: Specific module access based on responsibilities
- **General User**: Limited access to basic functions

### Document Types and Approval Workflows
- **Policies**: Organizational level → Management review
- **Procedures**: Operational details → Responsible party review
- **Instructions**: Specific guides → Technical approval
- **Records**: Activity evidence → Automatic validation
- **Meeting Minutes**: Committee records → Digital signature

## Key Workflows to Implement

### Risk Management Flow
Create risk → Assess impact/probability → Define treatment → Periodic review

### Incident Management Flow
Report → Classify → Analyze → Resolve → Document lessons learned

### Non-Conformity Flow
Detect → Register → Root cause analysis → Define corrective actions → Verify effectiveness

### Audit Flow
Plan → Execute → Record findings → Assign actions → Close audit

### SOA Management Flow
Select applicable controls → Justify inclusion/exclusion → Version control → Compare versions

## Database Considerations

Key entities to model:
- Users, Roles, Permissions
- SOA Controls (ISO 27001 Annex A)
- Risks, Assets, Treatments
- Documents with version control
- Incidents, Non-conformities
- Audits, Findings, Actions
- Tasks, Training sessions
- KPIs and metrics

## Security Requirements

- Password encryption and secure authentication
- Input validation and CSRF protection
- Audit logging for all changes
- GDPR compliance considerations
- Role-based access control enforcement

## Language and Localization

- Primary language: Spanish
- Design for potential multi-language support
- All user interfaces and documentation in Spanish

## Important Notes for Development

- Use Flask Blueprints for modular organization
- Implement comprehensive audit trails
- Focus on usability for non-technical security professionals
- Ensure all workflows support the complete ISMS lifecycle
- Performance target: <1s response time for common operations
- Plan for Docker containerization from the start

## Project Status

This project is in the initial planning phase. The codebase needs to be implemented following the specifications outlined above.