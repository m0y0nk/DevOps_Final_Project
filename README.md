# LabTrack — Laboratory Equipment & Inventory Management System
> **DevOps Final Capstone Project (100/100 Rubric Implementation)**
> **Author:** Mayank Soni | **GitHub:** [m0y0nk/DevOps_Final_Project](https://github.com/m0y0nk/DevOps_Final_Project)

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
├── .github/
│   └── workflows/
│       └── ci.yml                 # GitHub Actions CI/CD Pipeline
├── backend/
│   ├── app/
│   │   ├── api/endpoints.py       # REST API Endpoints (Items, Checkouts, Stats)
│   │   ├── core/config.py         # Application configuration & env settings
│   │   ├── db/session.py          # SQLAlchemy engine & session factory
│   │   ├── models/item.py         # SQLAlchemy & Pydantic models
│   │   └── main.py                # FastAPI app & Prometheus middleware
│   ├── migrations/                # Alembic database migrations
│   ├── tests/
│   │   └── test_api.py            # Pytest test suite (6 test cases)
│   ├── Dockerfile                 # Multi-stage non-root backend image
│   └── requirements.txt           # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/            # React UI components (Dashboard, Modal, etc.)
│   │   ├── App.jsx                # Main application component
│   │   └── index.css              # Custom styling & modern design tokens
│   ├── nginx.conf                 # Production Nginx reverse-proxy config
│   └── Dockerfile                 # Multi-stage non-root frontend image
├── helm/
│   └── labtrack/                  # Complete Helm chart (Deployments, Services, Ingress, HPA)
├── k8s/
│   └── namespace.yaml             # Kubernetes namespace manifest
├── monitoring/
│   └── prometheus-values.yaml     # Helm values for kube-prometheus-stack
├── terraform/                     # Terraform HCL files for AWS VPC + EKS
│   ├── eks.tf
│   ├── vpc.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars.example
├── troubleshooting/               # Scenario manifests for incident debugging
│   ├── broken-deployment.yaml
│   └── fixed-deployment.yaml
├── docker-compose.yml             # Local multi-container development setup
├── GRADING.md                     # 100-Point Grading Rubric & Submission Requirements
└── README.md                      # Comprehensive Project Documentation
```

---

## 🏆 12. Verification & Grading Checklist

- [x] **M1 (Application):** Full-stack LabTrack app with FastAPI, React, PostgreSQL, 4+ REST API endpoints.
- [x] **M2 (Testing):** Pytest test suite with 6 comprehensive test cases passing 100%.
- [x] **M3 (Docker):** Non-root user in both Dockerfiles, multi-stage build on frontend.
- [x] **M4 (CI/CD):** GitHub Actions pipeline with test, build, scan, and push stages.
- [x] **M5 (DevSecOps):** Trivy container vulnerability scan passing in pipeline.
- [x] **M6 (GHCR):** Container images published to GitHub Container Registry.
- [x] **M7 (Terraform):** Complete AWS VPC + EKS cluster provisioned and verified with IaC.
- [x] **M8 (Kubernetes):** Helm chart deployed to EKS with 2 backend replicas, 2 frontend replicas, Ingress routing.
- [x] **M9 (Observability):** `/metrics` endpoint, Prometheus scraping via ServiceMonitor (`UP`), Grafana live panel.
- [x] **M10 (Documentation):** Complete README.md and project demo ready.
