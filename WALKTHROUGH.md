# LabTrack — DevOps Capstone Project Walkthrough & Evidence
> **Repository:** [m0y0nk/DevOps_Final_Project](https://github.com/m0y0nk/DevOps_Final_Project)  
> 📖 **Project Presentation:** [Presentation.pptx](./demo/Presentation.pptx)
> **Author:** Mayank Soni | **Target Region:** AWS \`ap-south-1\` (Mumbai)

---

## 🔬 Application: Frontend + Backend + Database

### Implementation Details
- **Backend (\`backend/app/\`):** Built with Python 3.12 and FastAPI. Implements complete CRUD for equipment catalog and checkouts:
  - \`GET /api/items\`: Filter and list equipment by status, category, location
  - \`POST /api/items\`: Register new laboratory devices
  - \`GET /api/items/{id}\`: Retrieve detailed device status
  - \`PUT /api/items/{id}\`: Update equipment records
  - \`DELETE /api/items/{id}\`: Decommission equipment
  - \`POST /api/items/{id}/checkout\`: Researcher checkout workflow
  - \`POST /api/checkouts/{id}/return\`: Equipment return workflow
  - \`GET /api/dashboard/stats\`: Real-time inventory and maintenance KPIs
  - \`GET /health\` & \`GET /ready\`: Liveness and DB readiness checks
- **Database Migrations (\`backend/alembic/\`):** Initial schema migration (\`001_initial_schema.py\`) managing \`items\`, \`checkouts\`, and \`maintenance_logs\` tables.
- **Frontend (\`frontend/\`):** Modern React 18 single-page application featuring laboratory inventory tables, KPI cards, equipment check-out/return modals, and live status filters.

![LabTrack Application Running](screenshots/docker_images/docker-evidence.png)
*Figure 1.1: Live LabTrack single-page web application displaying KPI cards, equipment status badges, and interactive inventory table.*

---

## 🧪 Testing: Pytest + Code Quality 

### Implementation Details
- **Test Configuration (\`backend/pytest.ini\`, \`backend/tests/conftest.py\`):** Uses an isolated in-memory SQLite database engine with custom session overrides to guarantee tests do not mutate persistent storage.
- **Test Suite (\`backend/tests/test_api.py\`):** 6 automated test cases covering:
  1. \`test_health_and_root_endpoints\`: System liveness and info checks
  2. \`test_create_and_get_item\`: Item creation and UUID validation
  3. \`test_filter_items_by_status\`: Query parameter filtering
  4. \`test_equipment_checkout_flow\`: Full checkout lifecycle
  5. \`test_equipment_return_flow\`: Device return & condition audit
  6. \`test_dashboard_statistics\`: Aggregated inventory statistics

### Visual Evidence

![Pytest Test Suite Output](screenshots/pytest.png)
*Figure 2.1: Terminal output showing all 6 Pytest test cases passing cleanly.*

---

## 📦 Git & GitHub

### Implementation Details
- **Repository URL:** [https://github.com/m0y0nk/DevOps_Final_Project](https://github.com/m0y0nk/DevOps_Final_Project)
- **Commit History:** Follows standard Conventional Commits convention (\`feat:\`, \`fix:\`, \`chore:\`, \`docs:\`, \`sec:\`).
- **Git Hygiene:** Strict \`.gitignore\` prevents committing \`.env\`, \`__pycache__\`, \`node_modules\`, \`.venv\`, \`terraform.tfstate\`, and sensitive credentials.


![Git Commit History](screenshots/github/1.png)
*Figure 3.1: Clean, conventional Git commit history displaying descriptive commit messages and pipeline status badges.*

![Git Commit History](screenshots/github/2.png)
*Figure 3.2: Clean, conventional Git commit history displaying descriptive commit messages and pipeline status badges.*

![Git Commit History](screenshots/github/3.png)
*Figure 3.3: Clean, conventional Git commit history displaying descriptive commit messages and pipeline status badges.*

---

## 🐳 Docker: Dockerfile + Compose

### Implementation Details
- **Backend Dockerfile:** Multi-stage build starting from \`python:3.12-slim\`. Sets up non-root system user \`appuser\` (UID \`1001\`).
- **Frontend Dockerfile:** Multi-stage build using \`node:20-alpine\` to compile static distribution assets, copied to \`nginx:1.27-alpine\` running as unprivileged user \`nginx\` (UID \`101\`).
- **Docker Compose (\`docker-compose.yml\`):** Orchestrates \`postgres:16-alpine\`, \`backend\`, and \`frontend\` with built-in healthchecks, dependency ordering, and volume persistence.

### Visual Evidence

![Docker Compose Build Initializing](screenshots/docker_images/1.png)
*Figure 4.1: \`docker compose up --build\` initializing container builds.*

![Docker Compose Images Built](screenshots/docker_images/2.png)
*Figure 4.2: Frontend and backend multi-stage images successfully built and database volume created.*

![Docker Compose Running](screenshots/docker_images/3.png)
*Figure 4.3: All containers (PostgreSQL, FastAPI Backend, React Frontend) healthy and serving requests.*

---

## 🔄 CI/CD: GitHub Actions Pipeline 

### Implementation Details
- **Workflow File (\`.github/workflows/ci-cd.yml\`):**
  - **Stage 1 (Test):** Executes Python 3.12 environment, installs dependencies, and runs \`pytest\`. Concurrently runs Node.js 20 build check for React.
  - **Stage 2 (Security Scan):** Builds images and runs Trivy container vulnerability scanner.
  - **Stage 3 (Publish to GHCR):** Authenticates with GitHub Container Registry, tagging images with both Git commit SHA (\`sha-<commit>\`) and \`latest\`.

![GitHub Actions Pipeline Success](screenshots/github_actions/passed.png)
*Figure 5.1: GitHub Actions pipeline showing complete green execution (Test → Build → Scan → Push).*

![GHCR Packages Published](screenshots/github/image8.png)
*Figure 5.2: GitHub Container Registry (GHCR) repository packages showing published images with immutable SHA tags.*

---

## 🛡️ DevSecOps: Trivy Security Scan

### Implementation Details
- **Scan Step:** Integrates \`aquasecurity/trivy-action@master\` targeting both backend and frontend images.
- **Failure Policy:** Configured with \`exit-code: 1\` and \`severity: HIGH,CRITICAL\`.
- **Trivy Analysis & Remediation:**
  - Base operating system vulnerabilities were minimized by adopting minimal distros (\`python:3.12-slim\` and \`nginx:alpine\`).
  - Known low-impact Starlette upstream issues documented in \`.trivyignore\` ensure that only critical, actionable vulnerabilities halt deployment.

### Visual Evidence

![Trivy Security Scan Logs](screenshots/github_actions/trivy_log.png)
*Figure 6.1: GitHub Actions log output for Trivy security scanner validating container images.*

---

## ☁️ Terraform: AWS Infrastructure as Code 

### Implementation Details
- **Terraform Configuration (\`terraform/\`):**
  - Modular structure: \`vpc.tf\` (or \`networking.tf\`), \`eks.tf\`, \`variables.tf\`, \`outputs.tf\`, \`providers.tf\`.
  - Provisions a dedicated VPC (\`10.0.0.0/16\`) with 2 public subnets across \`ap-south-1a\` and \`ap-south-1b\`.
  - Creates an Amazon EKS 1.30 cluster (\`labtrack-eks\`) with managed node group on \`t3.small\` ON_DEMAND instances using \`AL2023_x86_64_STANDARD\` AMI.
  - Implements clean teardown with \`terraform destroy\` to prevent runaway cloud expenses.

### Visual Evidence

![Terraform Init & Plan](screenshots/terraform/init_plan.png)
*Figure 7.1: \`terraform init\` initializing provider plugins and backend lockfile.*

![Terraform Plan](screenshots/terraform/plan.png)
*Figure 7.2: \`terraform plan\` detailing resources to be created.*

![Terraform Apply](screenshots/terraform/apply.png)
*Figure 7.3: \`terraform apply\` provisioning AWS VPC, Subnets, IAM roles, and EKS Cluster.*

![AWS EKS Cluster Console](screenshots/eks.png)
*Figure 7.4: AWS Management Console displaying the active \`labtrack-eks\` cluster in region \`ap-south-1\` (Mumbai).*

![AWS VPC Console](screenshots/vpc.png)
*Figure 7.5: AWS Management Console displaying the dedicated VPC (\`10.0.0.0/16\`), public subnets, and routing table.*

![AWS EKS Managed Node Group](screenshots/terraform/aws_console.png)
*Figure 7.6: AWS Console view of the \`labtrack-managed-nodes\` node group configuration.*

![Active Worker Nodes](screenshots/terraform/nodes_evidence.png)
*Figure 7.7: \`kubectl get nodes\` verifying worker nodes joined the cluster and are in \`Ready\` state.*

![Terraform Destroy Teardown](screenshots/destroy.png)
*Figure 7.8: \`terraform destroy\` output verifying complete infrastructure teardown to prevent cloud costs.*

---

## ☸️ Kubernetes + Helm 

### Implementation Details
- **Namespace (\`k8s/namespace.yaml\`):** Dedicated \`labtrack\` namespace.
- **Helm Chart (\`helm/labtrack/\`):**
  - **Backend:** 2 replicas, resource limits/requests, non-root user, liveness/readiness probes.
  - **Frontend:** 2 replicas, Nginx reverse proxy serving static React distribution.
  - **PostgreSQL:** In-cluster PostgreSQL instance using \`emptyDir: {}\` ephemeral volume for compatibility.
  - **Ingress:** Configured with \`ingressClassName: nginx\` routing \`/\` to frontend and \`/api\` to backend.
  - **Migrations:** Alembic migrations managed as a resilient post-install Hook with connection retry loop.
- **Ingress Controller:** Deployed \`ingress-nginx\` controller backed by AWS Classic/Network Load Balancer.

### Visual Evidence

![Namespace & Ingress Controller Installation](screenshots/kubernetes_and_helm/1.png)
*Figure 8.1: \`kubectl apply -f k8s/namespace.yaml\` and Helm installation of \`ingress-nginx\` controller.*

![Helm Chart Deployment](screenshots/kubernetes_and_helm/2.png)
*Figure 8.2: \`helm upgrade --install labtrack ./helm/labtrack\` deployment status showing \`deployed\`.*

![Application Live on Ingress LoadBalancer](screenshots/kubernetes_and_helm/3.png)
*Figure 8.3: Browser accessing live LabTrack application via the AWS LoadBalancer DNS endpoint (\`a14aff9319d1a45cd8ce8bb860ebb1d6-432578313.ap-south-1.elb.amazonaws.com\`)*

---

## 📊 Observability: Prometheus + Grafana 

### Implementation Details
- **Metrics Instrumentation:** FastAPI Prometheus client middleware exposes:
  - \`http_requests_total\`: HTTP requests partitioned by endpoint, method, and HTTP status code.
  - \`http_request_duration_seconds\`: Latency distribution histograms.
  - Python runtime GC and process memory stats.
- **Prometheus Operator Deployment:** Deployed \`kube-prometheus-stack\` configured via \`monitoring/prometheus-values.yaml\`.
- **Target Scraping:** \`ServiceMonitor\` in \`helm/labtrack/templates/servicemonitor.yaml\` discovers and scrapes backend pods every 15s.
- **Grafana Visualization:** Accessible via dedicated AWS LoadBalancer (\`a9887f4d6b0a04704a8b7222f528aa67-1051888215.ap-south-1.elb.amazonaws.com\`), plotting live \`http_requests_total\` time series.

### Visual Evidence

![Prometheus Helm Stack Installation](screenshots/monitoring/1.png)
*Figure 9.1: \`kube-prometheus-stack\` Helm release installation in \`monitoring\` namespace.*

![Terminal Curl /metrics Output](screenshots/monitoring/2.png)
*Figure 9.2: Terminal \`curl http://localhost:8000/metrics\` output showing Prometheus metric types and values.*

![Browser /metrics Endpoint](screenshots/monitoring/3.png)
*Figure 9.3: Browser view of the raw \`/metrics\` endpoint output.*

![Prometheus Targets UP](screenshots/monitoring/4.png)
*Figure 9.4: Prometheus Targets health dashboard confirming application endpoints in state \`UP\`.*

![Grafana Explore LoadBalancer](screenshots/monitoring/5.png)
*Figure 9.5: Grafana Explore dashboard accessed via AWS LoadBalancer endpoint.*

![Grafana Live Application Metrics Panel](screenshots/monitoring/6.png)
*Figure 9.6: Grafana live visualization displaying \`http_requests_total\` application query graph.*

---

## 📝 Final Presentation & Documentation 

### Implementation Details
- **Architecture & Operational Documentation:** [README.md](./README.md) provides an end-to-end guide detailing application domain, technology stack, local setup, CI/CD pipeline, Terraform IaC, Helm manifests, and monitoring setup.
- **Step-by-Step Evidence:** This [WALKTHROUGH.md](./WALKTHROUGH.md) serves as the complete verifiable record of all 10 milestones.