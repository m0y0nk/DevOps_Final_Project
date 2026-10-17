# LabTrack — Laboratory Equipment & Inventory Management System
> **DevOps Final Capstone Project**  
> **Author:** Mayank Soni | **GitHub:** [m0y0nk/DevOps_Final_Project](https://github.com/m0y0nk/DevOps_Final_Project)  
> 📖 **Project Walkthrough:** [WALKTHROUGH.md](./WALKTHROUGH.md)
> 📖 **Project Presentation:** [Presentation.pptx](./demo/Presentation.pptx)

---

## 🔬 1. Project Overview & Domain

**LabTrack** is a full-stack, enterprise-grade laboratory equipment and inventory management platform designed for academic and commercial research labs. It solves the critical operational challenge of tracking high-value shared instruments (e.g., spectrophotometers, centrifuges, PCR thermocyclers, optical microscopes), chemical reagents, maintenance calibrations, and researcher checkouts.

### Key Capabilities
- **Equipment Inventory Catalog:** Track devices, categories, serial numbers, locations (Lab Room, Bench #), status (`AVAILABLE`, `CHECKED_OUT`, `IN_MAINTENANCE`), and calibration expiry dates.
- **Equipment Checkout & Return Workflow:** Complete lifecycle tracking of which researcher checked out which item, expected return date, and condition upon return.
- **Maintenance & Calibration Alerts:** Immediate visual alerts when equipment requires recalibration or preventative maintenance.
- **RESTful API & Swagger Docs:** OpenAPI/Swagger compliant backend built with FastAPI and PostgreSQL.
- **Production Observability:** Built-in Prometheus middleware exporting custom HTTP latency, request count metrics, and system runtime statistics.

---

## 🏗️ 2. Architecture & DevOps Pipeline

```
                                  DEVELOPER WORKFLOW
                                          │
                                   [ Git Commit ]
                                          │
                                          ▼
                                   [ GitHub Actions ]
                                ┌─────────┴─────────┐
                                ▼                   ▼
                        [ Backend Pytest ]   [ Frontend Build ]
                                └─────────┬─────────┘
                                          ▼
                               [ Docker Multi-Stage Build ]
                                          ▼
                                [ Trivy Vulnerability Scan ]
                                          ▼
                                [ Publish to GitHub GHCR ]
                                          │
                                          ▼
                              AWS CLOUD INFRASTRUCTURE
                        ┌───────────────────────────────────┐
                        │  VPC (10.0.0.0/16, ap-south-1)    │
                        │    ├── Public Subnet 1 (AZ 1a)    │
                        │    ├── Public Subnet 2 (AZ 1b)    │
                        │    └── AWS EKS Cluster (v1.30)    │
                        │          └── Managed Nodes        │
                        └─────────────────┬─────────────────┘
                                          │
                            KUBERNETES & HELM DEPLOYMENT
                                          ▼
                               [ Nginx Ingress Controller ]
                                ┌─────────┴─────────┐
                                ▼                   ▼
                       [ React Frontend ]   [ FastAPI Backend ]
                           (2 Replicas)         (2 Replicas)
                                │                   │
                                └─────────┬─────────┘
                                          ▼
                                [ PostgreSQL Database ]
                                          ▲
                                          │
                               OBSERVABILITY STACK
                                          │
                        ┌─────────────────┴─────────────────┐
                        ▼                                   ▼
              [ Prometheus Server ]               [ Grafana Dashboards ]
              (ServiceMonitor: /metrics)          (Live Latency & Traffic)
```

---

## 🛠️ 3. Tech Stack

| Layer | Technologies & Tools |
|---|---|
| **Frontend** | React 18, Vite, Lucide Icons, Custom Design System, Nginx 1.27 Alpine |
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic, Prometheus Client |
| **Database** | PostgreSQL 16 Alpine |
| **Containerization** | Docker, Multi-Stage Builds, Non-Root Linux Users (`appuser:1001`, `nginx:101`) |
| **CI/CD & Security** | GitHub Actions, Trivy Container Scanner, GitHub Container Registry (GHCR) |
| **Infrastructure (IaC)**| Terraform 1.7+, AWS VPC, AWS EKS (Kubernetes 1.30), AWS Managed Node Groups |
| **Orchestration** | Kubernetes, Helm 3, Ingress-Nginx, Horizontal Pod Autoscaler (HPA) |
| **Monitoring** | Prometheus Operator (`kube-prometheus-stack`), Grafana |

---

## 🚀 4. Local Development Quickstart

### Prerequisites
- Docker Engine & Docker Compose (`v2.20+`)
- Python 3.12+ (for running tests locally)
- Node.js 20+

### Run the Application via Docker Compose
To run the full stack (PostgreSQL + FastAPI backend + React frontend) in one command:

```bash
docker compose up --build
```

- **Frontend Application:** [http://localhost:3000](http://localhost:3000)
- **FastAPI Interactive Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Prometheus Metrics:** [http://localhost:8000/metrics](http://localhost:8000/metrics)
- **Health Check Endpoint:** [http://localhost:8000/health](http://localhost:8000/health)

---

## 🧪 5. Testing & Quality Assurance (M2)

The backend includes a comprehensive `pytest` test suite with in-memory SQLite fixtures covering all CRUD and lifecycle operations:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest -v
```

### Test Coverage Highlights
- `test_health_and_root_endpoints`: Verifies system liveness and version endpoints.
- `test_create_and_get_item`: Tests inventory item creation, UUID generation, and retrieval.
- `test_filter_items_by_status`: Validates status filtering (`AVAILABLE`, `CHECKED_OUT`, `IN_MAINTENANCE`).
- `test_equipment_checkout_flow`: Tests the checkout workflow, status transition, and audit trail.
- `test_equipment_return_flow`: Tests item return and status reset to `AVAILABLE`.
- `test_dashboard_statistics`: Verifies aggregated counts for active equipment, checkouts, and maintenance alerts.

---

## 🐳 6. Docker Containerization (M3)

Both services are built adhering strictly to the **principle of least privilege** and production optimization:
- **Backend (`backend/Dockerfile`):**
  - Base: `python:3.12-slim`
  - Runs as non-root user `appuser` (UID: `1001`, GID: `1001`)
  - Cleans up pip cache to minimize image footprint.
- **Frontend (`frontend/Dockerfile`):**
  - **Stage 1 (Builder):** `node:20-alpine` builds production assets using Vite.
  - **Stage 2 (Runtime):** `nginx:1.27-alpine` serves static files and reverse proxies API traffic.
  - Runs as non-root user `nginx` (UID: `101`).

---

## 🔄 7. CI/CD & DevSecOps Pipeline (M4–M6)

GitHub Actions workflow located at `.github/workflows/ci.yml`:

1. **Test Stage:**
   - Runs `pytest` on backend.
   - Runs `npm run build` on frontend to verify TypeScript/Vite compilation.
2. **Security Scan (Trivy DevSecOps):**
   - Scans backend and frontend container images for CRITICAL vulnerabilities.
   - Outputs vulnerability report in pipeline logs.
3. **Container Registry Publish (GHCR):**
   - Authenticates to GitHub Container Registry using `GITHUB_TOKEN`.
   - Tags and publishes images with both `latest` and `SHA` tags:
     - `ghcr.io/m0y0nk/labtrack-backend:latest`
     - `ghcr.io/m0y0nk/labtrack-frontend:latest`

---

## ☁️ 8. Infrastructure as Code: Terraform on AWS (M7)

Located in `terraform/`:
- **VPC & Networking:** Dedicated VPC (`10.0.0.0/16`), 2 public subnets in different Availability Zones (`ap-south-1a`, `ap-south-1b`), Internet Gateway, and route tables.
- **IAM Roles:** Minimal IAM roles for EKS Cluster control plane and EKS worker nodes.
- **EKS Cluster:** Kubernetes version `1.30` with public endpoint access.
- **Node Group:** Managed Node Group utilizing cost-efficient `t3.small` instances with auto-scaling (`min=1`, `desired=2`, `max=3`).

### Terraform Execution
```bash
cd terraform
terraform init
terraform plan
terraform apply -auto-approve
terraform destroy -auto-approve
```

---

## ☸️ 9. Kubernetes & Helm Deployment (M8)

The application is packaged as a production Helm chart in `helm/labtrack/`:
- **Namespaces:** Isolated `labtrack` namespace (`k8s/namespace.yaml`).
- **Deployments:**
  - `labtrack-backend` (2 replicas, CPU/Memory limits, non-root securityContext, liveness & readiness probes).
  - `labtrack-frontend` (2 replicas, Nginx serving SPA).
  - `labtrack-postgresql` (dedicated in-cluster PostgreSQL instance).
- **Services:** ClusterIP services exposing backend on 8000, frontend on 8080, postgresql on 5432.
- **Ingress:** Nginx Ingress routing `/` to the React frontend and `/api` to the FastAPI backend.
- **Autoscaling (HPA):** Horizontal Pod Autoscaler targeting 80% CPU utilization.

### Deployment Commands
```bash
kubectl apply -f k8s/namespace.yaml
helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx -n ingress-nginx --create-namespace
helm upgrade --install labtrack ./helm/labtrack -n labtrack --create-namespace
```

---

## 📊 10. Observability: Prometheus + Grafana (M9)

### Metrics Architecture
- Backend exposes Prometheus metrics at `/metrics` using `prometheus_client`.
- Custom metrics tracked:
  - `http_requests_total`: Total HTTP requests labeled by `method`, `endpoint`, and `status_code`.
  - `http_request_duration_seconds`: Histogram of request latency.
  - Python GC and process memory/CPU statistics.
- **Prometheus Operator:** Scrapes backend pods every 15 seconds via custom `ServiceMonitor`.
- **Grafana:** Visualizes live application traffic, latency histograms, and system health.

---

## 📁 11. Project Directory Structure

```text
.
├── .dockerignore                  # Docker build exclusions
├── .env.example                   # Environment configuration template
├── .github/
│   └── workflows/
│       └── ci-cd.yml              # GitHub Actions CI/CD Pipeline
├── .trivyignore                   # Trivy vulnerability filter rules
├── GRADING.md                     # 100-Point Grading Rubric & Submission Requirements
├── README.md                      # Primary Project Documentation
├── WALKTHROUGH.md                 # Complete Step-by-Step Evidence & Screenshots Guide
├── backend/
│   ├── Dockerfile                 # Multi-stage non-root Python 3.12 image
│   ├── alembic/                   # Database migrations
│   │   ├── env.py
│   │   └── versions/
│   │       └── 001_initial_schema.py
│   ├── alembic.ini
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints.py       # REST API Endpoints (Items, Checkouts, Stats)
│   │   ├── core/
│   │   │   └── config.py          # Application configuration & env settings
│   │   ├── db/
│   │   │   └── session.py         # SQLAlchemy engine & session factory
│   │   ├── models/                # Database models
│   │   │   ├── __init__.py
│   │   │   └── models.py
│   │   ├── schemas/               # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   └── schemas.py
│   │   ├── services/              # Business logic services
│   │   │   └── services.py
│   │   └── main.py                # FastAPI app & Prometheus metrics middleware
│   ├── pytest.ini                 # Pytest test runner configuration
│   ├── requirements.txt           # Python backend dependencies
│   └── tests/
│       ├── conftest.py            # SQLite test database fixtures
│       └── test_api.py            # Automated API test suite (6 test cases)
├── docker-compose.yml             # Local multi-container development environment
├── docs/
│   └── SPEC.md                    # Project requirements and domain specification
├── frontend/
│   ├── Dockerfile                 # Multi-stage Node.js build -> Nginx Alpine runtime
│   ├── index.html
│   ├── nginx.conf                 # Nginx reverse proxy configuration
│   ├── package-lock.json
│   ├── package.json
│   ├── src/
│   │   ├── App.jsx                # Main React UI component
│   │   ├── index.css              # Custom styling & design system tokens
│   │   └── main.jsx               # Application entrypoint
│   └── vite.config.js             # Vite development & build configuration
├── helm/
│   └── labtrack/                  # Complete Kubernetes Helm Chart
│       ├── Chart.yaml             # Chart metadata
│       ├── templates/
│       │   ├── _helpers.tpl
│       │   ├── deployment-backend.yaml
│       │   ├── deployment-frontend.yaml
│       │   ├── deployment-postgres.yaml
│       │   ├── hpa.yaml           # Horizontal Pod Autoscaler
│       │   ├── ingress.yaml       # Ingress routing rules
│       │   ├── job-migration.yaml # Alembic DB migration post-install Hook
│       │   ├── secret.yaml        # Database credentials secret
│       │   └── servicemonitor.yaml# Prometheus Operator ServiceMonitor
│       ├── values-dev.yaml        # Development values overlay
│       └── values.yaml            # Default chart values
├── k8s/
│   └── namespace.yaml             # Dedicated Kubernetes namespace manifest
├── monitoring/
│   └── prometheus-values.yaml     # Helm values for kube-prometheus-stack
├── screenshots/                   # Verification Evidence Screenshots (M1-M9)
├── scripts/
│   └── seed_demo_data.py          # Demo database seeder script
├── terraform/                     # AWS Infrastructure as Code (Terraform)
│   ├── .terraform.lock.hcl
│   ├── README.md                  # Terraform instructions
│   ├── eks.tf                     # Amazon EKS 1.30 & Worker Node Group
│   ├── networking.tf              # AWS VPC, Subnets, Route Tables, IGW
│   ├── outputs.tf                 # Cluster and VPC output values
│   ├── providers.tf               # AWS provider configuration
│   ├── terraform.tfvars.example   # Example variables template (no secrets)
│   ├── variables.tf               # Infrastructure variables
│   └── versions.tf                # Required provider versions
└── troubleshooting/               # Failure recovery exercises
    ├── broken-deployment.yaml
    └── fixed-deployment.yaml
```

---

## 🏆 12. Complete Walkthrough

For the complete, illustrated step-by-step documentation covering each of the 10 rubric milestones with embedded screenshot evidence and command explanations, please see:

👉 **[WALKTHROUGH.md](./WALKTHROUGH.md)**
