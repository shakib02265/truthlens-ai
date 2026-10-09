# TruthLens AI - API Documentation

## Authentication Endpoints
- `POST /api/auth/register`: Register user account
- `POST /api/auth/login`: Authenticate and receive JWT token
- `GET /api/auth/me`: Get current authenticated user profile

## Investigation Endpoints
- `POST /api/investigations`: Submit a new claim for investigation
- `GET /api/investigations`: List user investigations
- `GET /api/investigations/{id}`: Get full investigation details
- `DELETE /api/investigations/{id}`: Delete investigation record
- `POST /api/investigations/{id}/run`: Run or re-run investigation graph
- `POST /api/investigations/{id}/stop`: Cancel running investigation
- `GET /api/investigations/{id}/sources`: Retrieve evaluated sources
- `GET /api/investigations/{id}/evidence`: Retrieve extracted evidence statements
- `GET /api/investigations/{id}/graph`: Get interactive evidence graph payload
- `GET /api/investigations/{id}/trace`: Get execution agent trace history
- `GET /api/investigations/{id}/stream`: SSE endpoint for real-time live execution tracing
- `POST /api/investigations/{id}/review`: Submit human review decision
- `POST /api/investigations/{id}/report?format=pdf|html`: Export report file

## Dashboard Stats Endpoint
- `GET /api/investigations/dashboard/stats`: Returns aggregated stats, average confidence, and verdict distribution.
