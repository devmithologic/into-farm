# Kubernetes Practice Lab - Platform Operations Focus

## Prerequisites

You'll need either:
- **minikube**: `minikube start --cpus 2 --memory 4096`
- **kind**: `kind create cluster --name practice`
- **Docker Desktop** with Kubernetes enabled

Verify: `kubectl cluster-info`

---

## Lab 1: RBAC Deep Dive (Critical for this role!)

### Scenario
You need to give a CI/CD service account permission to deploy applications in staging but NOT production.

### Setup: Create Lab Directory

```bash
# Create directory structure for lab files
mkdir -p ~/k8s-lab/lab1
cd ~/k8s-lab/lab1
```

### Step 1: Create Namespaces

```bash
# Create staging and production namespaces
kubectl create namespace staging
kubectl create namespace production

# Add labels for organization
kubectl label namespace staging environment=staging
kubectl label namespace production environment=production

# Verify
kubectl get namespaces --show-labels
```

### Step 2: Create Service Account

```bash
# Create SA for CI/CD pipeline
kubectl create serviceaccount cicd-deployer -n staging

# Verify
kubectl get serviceaccount -n staging
```

### Step 3: Create Role (namespace-scoped permissions)

```bash
# Create the YAML file
cat > deployment-manager-role.yml << 'EOF'
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: deployment-manager
  namespace: staging
rules:
  # Can manage deployments
  - apiGroups: ["apps"]
    resources: ["deployments", "replicasets"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
  # Can view pods and logs (for troubleshooting)
  - apiGroups: [""]
    resources: ["pods", "pods/log"]
    verbs: ["get", "list", "watch"]
  # Can manage services
  - apiGroups: [""]
    resources: ["services"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
  # Can manage configmaps
  - apiGroups: [""]
    resources: ["configmaps"]
    verbs: ["get", "list", "watch", "create", "update", "patch"]
  # CANNOT manage secrets (security best practice)
EOF

# Review the file
cat deployment-manager-role.yml

# Apply it
kubectl apply -f deployment-manager-role.yml
```

### Step 4: Bind Role to ServiceAccount

```bash
# Create the YAML file
cat > cicd-deployer-binding.yml << 'EOF'
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: cicd-deployer-binding
  namespace: staging
subjects:
  - kind: ServiceAccount
    name: cicd-deployer
    namespace: staging
roleRef:
  kind: Role
  name: deployment-manager
  apiGroup: rbac.authorization.k8s.io
EOF

# Review the file
cat cicd-deployer-binding.yml

# Apply it
kubectl apply -f cicd-deployer-binding.yml
```

### Step 5: Test Permissions

```bash
# Check what the service account can do
kubectl auth can-i --list --as=system:serviceaccount:staging:cicd-deployer -n staging

# Test specific permissions
kubectl auth can-i create deployments --as=system:serviceaccount:staging:cicd-deployer -n staging
# Should return: yes

kubectl auth can-i create secrets --as=system:serviceaccount:staging:cicd-deployer -n staging
# Should return: no

kubectl auth can-i create deployments --as=system:serviceaccount:staging:cicd-deployer -n production
# Should return: no (no binding in production!)
```

### Step 6: Use the ServiceAccount

```bash
# Create a test deployment YAML file
cat > nginx-staging-deployment.yml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-staging
  namespace: staging
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
        - name: nginx
          image: nginx:1.21
          ports:
            - containerPort: 80
EOF

# Review the file
cat nginx-staging-deployment.yml

# Apply as the service account (should succeed)
kubectl apply --as=system:serviceaccount:staging:cicd-deployer -f nginx-staging-deployment.yml

# Create a deployment for production (to test denial)
cat > nginx-prod-deployment.yml << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-prod
  namespace: production
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
        - name: nginx
          image: nginx:1.21
          ports:
            - containerPort: 80
EOF

# Try to apply as the service account (should fail!)
kubectl apply --as=system:serviceaccount:staging:cicd-deployer -f nginx-prod-deployment.yml
# Expected: Error - forbidden
```

### List All Created Files

```bash
# See all YAML files you created
ls -la ~/k8s-lab/lab1/

# You should see:
# deployment-manager-role.yml
# cicd-deployer-binding.yml
# nginx-staging-deployment.yml
# nginx-prod-deployment.yml
```

### RBAC Interview Practice Questions

1. **"What's the difference between Role and ClusterRole?"**
   - Role is namespace-scoped (only one namespace)
   - ClusterRole is cluster-scoped (all namespaces + cluster resources like nodes)

2. **"What's the difference between RoleBinding and ClusterRoleBinding?"**
   - RoleBinding binds in ONE namespace (even if referencing a ClusterRole)
   - ClusterRoleBinding binds across ALL namespaces

3. **"How do you give someone admin access to only their namespace?"**
   - Create RoleBinding in their namespace that references the built-in `admin` ClusterRole

```bash
# Example: Give user 'dev-team' admin in staging namespace
kubectl create rolebinding dev-admin \
  --clusterrole=admin \
  --group=dev-team \
  --namespace=staging
```

---


## Lab 1B: ClusterRole & ClusterRoleBinding (Advanced RBAC)

### Understanding the Difference

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         RBAC SCOPE COMPARISON                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Role + RoleBinding                ClusterRole + ClusterRoleBinding     │
│  ─────────────────                 ────────────────────────────────     │
│                                                                         │
│  ┌─────────────┐                   ┌─────────────────────────────────┐  │
│  │ Namespace A │                   │        ENTIRE CLUSTER           │  │
│  │  ┌───────┐  │                   │                                 │  │
│  │  │ Role  │  │                   │  ┌─────────┐   ┌─────────┐      │  │
│  │  └───────┘  │                   │  │Namespace│   │Namespace│      │  │
│  │      ↓      │                   │  │    A    │   │    B    │      │  │
│  │  ┌────────┐ │                   │  └─────────┘   └─────────┘      │  │
│  │  │Binding │ │                   │                                 │  │
│  │  └────────┘ │                   │  + Cluster resources:           │  │
│  └─────────────┘                   │    nodes, PVs, namespaces       │  │
│                                    └─────────────────────────────────┘  │
│  Can only access                   Can access ALL namespaces            │
│  resources in                      AND cluster-scoped resources         │
│  Namespace A                                                            │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ClusterRole + RoleBinding (HYBRID - very useful!)                      │
│  ────────────────────────────────────────────────                       │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────┐        │
│  │ ClusterRole (defined once, reusable)                        │        │
│  │ "pod-reader" - can get/list/watch pods                      │        │
│  └─────────────────────────────────────────────────────────────┘        │
│           │                              │                              │
│           ▼                              ▼                              │
│  ┌─────────────────┐           ┌─────────────────┐                      │
│  │ RoleBinding     │           │ RoleBinding     │                      │
│  │ in namespace A  │           │ in namespace B  │                      │
│  │ → user can read │           │ → user can read │                      │
│  │   pods in A     │           │   pods in B     │                      │
│  └─────────────────┘           └─────────────────┘                      │
│                                                                         │
│  Same ClusterRole, different RoleBindings = granular control            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Setup: Create Lab Directory

```bash
# Create directory structure for lab files
mkdir -p ~/k8s-lab/lab1b
cd ~/k8s-lab/lab1b
```

### Scenario 1: Cluster-Wide Read-Only Monitoring

You need to give a monitoring service account (like Prometheus) read access to pods, nodes, and endpoints across ALL namespaces.

**Step 1: Create the namespace and ServiceAccount**

```bash
kubectl create namespace monitoring
kubectl create serviceaccount prometheus-sa -n monitoring
```

**Step 2: Create the ClusterRole YAML file**

```bash
# Create the file
cat > cluster-monitoring-reader.yml << 'EOF'
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-monitoring-reader
rules:
  # Read pods across all namespaces
  - apiGroups: [""]
    resources: ["pods", "pods/log", "services", "endpoints"]
    verbs: ["get", "list", "watch"]
  # Read deployments and replicasets
  - apiGroups: ["apps"]
    resources: ["deployments", "replicasets", "daemonsets", "statefulsets"]
    verbs: ["get", "list", "watch"]
  # Read nodes (cluster-scoped resource!)
  - apiGroups: [""]
    resources: ["nodes", "nodes/metrics", "nodes/stats"]
    verbs: ["get", "list", "watch"]
  # Read namespaces themselves
  - apiGroups: [""]
    resources: ["namespaces"]
    verbs: ["get", "list", "watch"]
  # Read events for alerting
  - apiGroups: [""]
    resources: ["events"]
    verbs: ["get", "list", "watch"]
EOF

# Review the file
cat cluster-monitoring-reader.yml

# Apply it
kubectl apply -f cluster-monitoring-reader.yml
```

**Step 3: Create the ClusterRoleBinding YAML file**

```bash
# Create the file
cat > prometheus-cluster-binding.yml << 'EOF'
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: prometheus-cluster-reader
subjects:
  - kind: ServiceAccount
    name: prometheus-sa
    namespace: monitoring
roleRef:
  kind: ClusterRole
  name: cluster-monitoring-reader
  apiGroup: rbac.authorization.k8s.io
EOF

# Review the file
cat prometheus-cluster-binding.yml

# Apply it
kubectl apply -f prometheus-cluster-binding.yml
```

**Step 4: Test permissions**

```bash
# Can read pods in ANY namespace
kubectl auth can-i list pods --as=system:serviceaccount:monitoring:prometheus-sa -n staging
kubectl auth can-i list pods --as=system:serviceaccount:monitoring:prometheus-sa -n production
kubectl auth can-i list pods --as=system:serviceaccount:monitoring:prometheus-sa -n kube-system
# All should return: yes

# Can read nodes (cluster-scoped)
kubectl auth can-i list nodes --as=system:serviceaccount:monitoring:prometheus-sa
# Should return: yes

# CANNOT create or delete anything
kubectl auth can-i delete pods --as=system:serviceaccount:monitoring:prometheus-sa -n staging
kubectl auth can-i create deployments --as=system:serviceaccount:monitoring:prometheus-sa -n staging
# Both should return: no
```

---

### Scenario 2: Cluster Admin for Platform Team

Create a ClusterRole for platform engineers who need broad access but shouldn't touch certain sensitive namespaces.

**Step 1: Create the ServiceAccount**

```bash
kubectl create serviceaccount platform-engineer -n default
```

**Step 2: Create the ClusterRole YAML file**

```bash
# Create the file
cat > platform-engineer-clusterrole.yml << 'EOF'
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: platform-engineer
rules:
  # Full access to workloads
  - apiGroups: ["apps"]
    resources: ["deployments", "replicasets", "daemonsets", "statefulsets"]
    verbs: ["*"]
  # Full access to core resources
  - apiGroups: [""]
    resources: ["pods", "services", "configmaps", "persistentvolumeclaims"]
    verbs: ["*"]
  # Read-only on secrets (security best practice)
  - apiGroups: [""]
    resources: ["secrets"]
    verbs: ["get", "list", "watch"]
  # Can manage ingresses
  - apiGroups: ["networking.k8s.io"]
    resources: ["ingresses", "networkpolicies"]
    verbs: ["*"]
  # Can view nodes but not modify
  - apiGroups: [""]
    resources: ["nodes"]
    verbs: ["get", "list", "watch"]
  # Can manage HPAs
  - apiGroups: ["autoscaling"]
    resources: ["horizontalpodautoscalers"]
    verbs: ["*"]
  # CANNOT manage RBAC (prevent privilege escalation)
  # CANNOT manage namespaces (prevent creating new ones)
EOF

# Review and apply
cat platform-engineer-clusterrole.yml
kubectl apply -f platform-engineer-clusterrole.yml
```

**Step 3: Create RoleBindings for specific namespaces (HYBRID approach)**

```bash
# Create RoleBinding for staging namespace
cat > platform-engineer-staging-binding.yml << 'EOF'
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: platform-engineer-staging
  namespace: staging
subjects:
  - kind: ServiceAccount
    name: platform-engineer
    namespace: default
roleRef:
  kind: ClusterRole  # Note: ClusterRole, not Role!
  name: platform-engineer
  apiGroup: rbac.authorization.k8s.io
EOF

# Create RoleBinding for production namespace
cat > platform-engineer-production-binding.yml << 'EOF'
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: platform-engineer-production
  namespace: production
subjects:
  - kind: ServiceAccount
    name: platform-engineer
    namespace: default
roleRef:
  kind: ClusterRole
  name: platform-engineer
  apiGroup: rbac.authorization.k8s.io
EOF

# Review and apply both
cat platform-engineer-staging-binding.yml
cat platform-engineer-production-binding.yml

kubectl apply -f platform-engineer-staging-binding.yml
kubectl apply -f platform-engineer-production-binding.yml
```

**Step 4: Test - has access to staging and production, NOT kube-system**

```bash
kubectl auth can-i create deployments --as=system:serviceaccount:default:platform-engineer -n staging
# yes

kubectl auth can-i create deployments --as=system:serviceaccount:default:platform-engineer -n production
# yes

kubectl auth can-i create deployments --as=system:serviceaccount:default:platform-engineer -n kube-system
# no! (no RoleBinding in kube-system)

kubectl auth can-i delete secrets --as=system:serviceaccount:default:platform-engineer -n staging
# no (only read access to secrets)
```

---

### Scenario 3: Node Administrator (Cluster-Scoped Resources)

Some resources like nodes, persistent volumes, and namespaces are cluster-scoped. You need ClusterRole + ClusterRoleBinding to manage them.

**Step 1: Create the ServiceAccount**

```bash
kubectl create serviceaccount infra-admin -n default
```

**Step 2: Create the ClusterRole YAML file**

```bash
# Create the file
cat > infrastructure-admin-clusterrole.yml << 'EOF'
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: infrastructure-admin
rules:
  # Manage nodes
  - apiGroups: [""]
    resources: ["nodes"]
    verbs: ["get", "list", "watch", "patch", "update"]
  # Manage persistent volumes (cluster-scoped)
  - apiGroups: [""]
    resources: ["persistentvolumes"]
    verbs: ["*"]
  # Manage storage classes
  - apiGroups: ["storage.k8s.io"]
    resources: ["storageclasses"]
    verbs: ["*"]
  # View namespaces
  - apiGroups: [""]
    resources: ["namespaces"]
    verbs: ["get", "list", "watch"]
  # Manage cluster-level network policies
  - apiGroups: ["networking.k8s.io"]
    resources: ["networkpolicies"]
    verbs: ["*"]
EOF

# Review and apply
cat infrastructure-admin-clusterrole.yml
kubectl apply -f infrastructure-admin-clusterrole.yml
```

**Step 3: Create the ClusterRoleBinding YAML file**

```bash
# Create the file
cat > infra-admin-binding.yml << 'EOF'
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: infra-admin-binding
subjects:
  - kind: ServiceAccount
    name: infra-admin
    namespace: default
roleRef:
  kind: ClusterRole
  name: infrastructure-admin
  apiGroup: rbac.authorization.k8s.io
EOF

# Review and apply
cat infra-admin-binding.yml
kubectl apply -f infra-admin-binding.yml
```

**Step 4: Test cluster-scoped permissions**

```bash
kubectl auth can-i list nodes --as=system:serviceaccount:default:infra-admin
# yes

kubectl auth can-i create persistentvolumes --as=system:serviceaccount:default:infra-admin
# yes

# But cannot manage workloads
kubectl auth can-i create deployments --as=system:serviceaccount:default:infra-admin -n staging
# no
```

---

### Scenario 4: Aggregated ClusterRoles (Advanced)

Kubernetes has built-in label-based aggregation. You can extend existing roles.

**Step 1: Create the aggregated ClusterRole YAML file**

```bash
# Create the file
cat > custom-metrics-viewer.yml << 'EOF'
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: custom-metrics-viewer
  labels:
    # This label makes it aggregate into the built-in 'view' ClusterRole
    rbac.authorization.k8s.io/aggregate-to-view: "true"
rules:
  # Anyone with 'view' ClusterRole can now also see custom metrics
  - apiGroups: ["custom.metrics.k8s.io"]
    resources: ["*"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["metrics.k8s.io"]
    resources: ["pods", "nodes"]
    verbs: ["get", "list", "watch"]
EOF

# Review and apply
cat custom-metrics-viewer.yml
kubectl apply -f custom-metrics-viewer.yml
```

**Step 2: Verify aggregation**

```bash
# Now anyone bound to 'view' automatically gets these permissions too!
# Check what 'view' includes now:
kubectl describe clusterrole view | grep -A5 "custom.metrics"
```

---

### Scenario 5: Emergency Break-Glass Access

Create a highly privileged role for emergency situations with audit logging.

**Step 1: Create the emergency ClusterRole YAML file**

```bash
# Create the file
cat > emergency-responder-clusterrole.yml << 'EOF'
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: emergency-responder
  annotations:
    description: "Break-glass access for P1 incidents. Usage is audited."
rules:
  # Almost full access
  - apiGroups: ["*"]
    resources: ["*"]
    verbs: ["*"]
  # Note: RBAC is intentionally NOT excluded here
  # In production, you'd want more granular control
EOF

# Review and apply
cat emergency-responder-clusterrole.yml
kubectl apply -f emergency-responder-clusterrole.yml
```

**Step 2: Create a temporary binding for an incident (with metadata)**

```bash
# Create the file - note the annotations for audit trail
cat > emergency-incident-12345-binding.yml << 'EOF'
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: emergency-incident-12345
  annotations:
    incident-id: "INC12345"
    expires: "2024-01-15T12:00:00Z"
    approved-by: "oncall-manager"
    reason: "Production database outage - need full access for recovery"
subjects:
  - kind: User
    name: oncall-engineer@company.com
    apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: emergency-responder
  apiGroup: rbac.authorization.k8s.io
EOF

# Review the file (don't apply unless you want to test)
cat emergency-incident-12345-binding.yml

# To apply (careful - this grants admin access!):
# kubectl apply -f emergency-incident-12345-binding.yml

# After incident, clean up:
# kubectl delete -f emergency-incident-12345-binding.yml
```

---

### List All Created Files

```bash
# See all YAML files you created
ls -la ~/k8s-lab/lab1b/

# You should see:
# cluster-monitoring-reader.yml
# prometheus-cluster-binding.yml
# platform-engineer-clusterrole.yml
# platform-engineer-staging-binding.yml
# platform-engineer-production-binding.yml
# infrastructure-admin-clusterrole.yml
# infra-admin-binding.yml
# custom-metrics-viewer.yml
# emergency-responder-clusterrole.yml
# emergency-incident-12345-binding.yml
```

### Apply All at Once (Alternative)

```bash
# You can also apply all files in the directory
kubectl apply -f ~/k8s-lab/lab1b/

# Or use kustomize-style organization
# kubectl apply -k ~/k8s-lab/lab1b/
```

### Quick Reference: Built-in ClusterRoles

```bash
# View all built-in ClusterRoles
kubectl get clusterroles | grep -E "^(admin|edit|view|cluster-admin)"

# What can 'view' do?
kubectl describe clusterrole view

# What can 'edit' do?
kubectl describe clusterrole edit

# What can 'admin' do? (namespace-level admin)
kubectl describe clusterrole admin

# What can 'cluster-admin' do? (GOD MODE - use carefully!)
kubectl describe clusterrole cluster-admin
```

### ClusterRole Interview Questions

**Q1: "When would you use ClusterRole vs Role?"**

**Answer**: "Use Role when permissions should be limited to a single namespace - like app deployments. Use ClusterRole when you need:
1. Access to cluster-scoped resources (nodes, PVs, namespaces)
2. Access across multiple namespaces
3. A reusable permission template that can be bound per-namespace with RoleBindings"

**Q2: "How do you prevent privilege escalation in RBAC?"**

**Answer**: "Several strategies:
1. Never give `*` verbs on RBAC resources
2. Use RoleBindings instead of ClusterRoleBindings when possible
3. Separate read and write permissions
4. Don't allow `escalate` or `bind` verbs on roles
5. Audit RBAC periodically with `kubectl auth can-i --list`"

**Q3: "What's the difference between ClusterRoleBinding and using RoleBinding with a ClusterRole?"**

**Answer**: "ClusterRoleBinding grants the ClusterRole's permissions cluster-wide - in every namespace plus cluster-scoped resources. RoleBinding with a ClusterRole grants those permissions only in the specific namespace where the RoleBinding exists. The second approach is useful for reusable role templates with namespace-level control."

### Cleanup Lab 1B

```bash
# Remove ClusterRoles
kubectl delete clusterrole cluster-monitoring-reader platform-engineer infrastructure-admin custom-metrics-viewer emergency-responder

# Remove ClusterRoleBindings
kubectl delete clusterrolebinding prometheus-cluster-reader infra-admin-binding

# Remove RoleBindings
kubectl delete rolebinding platform-engineer-staging -n staging
kubectl delete rolebinding platform-engineer-production -n production

# Remove ServiceAccounts
kubectl delete serviceaccount prometheus-sa -n monitoring
kubectl delete serviceaccount platform-engineer -n default
kubectl delete serviceaccount infra-admin -n default
kubectl delete namespace monitoring
```
