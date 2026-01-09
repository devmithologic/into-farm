# Kubernetes Troubleshooting: Deep Dive Study Guide

This guide documents key concepts and troubleshooting patterns learned through hands-on Kubernetes labs. Rather than just running commands, the goal is to understand *why* things fail and how to diagnose them systematically.

---

## Table of Contents

1. [Understanding Pod Failure States](#understanding-pod-failure-states)
2. [YAML Structure Fundamentals](#yaml-structure-fundamentals)
3. [The describe Command and Kubernetes Resources](#the-describe-command-and-kubernetes-resources)
4. [Labels vs Namespaces: Understanding the Difference](#labels-vs-namespaces-understanding-the-difference)

---

## Understanding Pod Failure States

When running troubleshooting labs, it's important to understand that the examples are intentionally crafted to produce specific errors. But what do these errors actually mean in production?

### CrashLoopBackOff

**What it really means:**

The pod successfully started, but the container inside keeps dying repeatedly. Kubernetes attempts to restart it, but it keeps failing. The "BackOff" part means Kubernetes incrementally increases the time between restart attempts (10s, 20s, 40s... up to 5 minutes) to avoid saturating resources.

**Common causes in production:**

| Cause | Description |
|-------|-------------|
| Application errors | Unhandled exceptions, code that crashes on startup |
| Missing configuration | Environment variables the app expects but don't exist, ConfigMaps or Secrets not mounted |
| OOMKilled | Application consumes more memory than allocated in `resources.limits` |
| Unavailable dependencies | App tries to connect to a database that doesn't exist or isn't ready |
| Incorrect command | The `command` or `entrypoint` specified doesn't exist or fails |
| Permissions | Process lacks permissions to write where it needs to |

### ImagePullBackOff

**What it really means:**

Kubernetes cannot download the container image. It doesn't even attempt to run the application.

**Common causes in production:**

| Cause | Description |
|-------|-------------|
| Image doesn't exist | Typo in name, incorrect tag, image was deleted from registry |
| Private registry without credentials | Missing `imagePullSecret` configuration |
| Inaccessible registry | Network issues, firewall blocking, registry down |
| Docker Hub rate limit | Docker Hub has pull limits for free accounts |
| Stale `latest` tag | Pull policy is `IfNotPresent` and there's an old cached version |

### Other Common Error States

| State | Meaning | Typical Causes |
|-------|---------|----------------|
| **Pending** | Pod accepted but cannot be scheduled | Insufficient resources (CPU/memory), node doesn't meet nodeSelector/affinity, PersistentVolume unavailable |
| **ContainerCreating** | Image downloaded but container won't start | Volume mount failing, Secret/ConfigMap doesn't exist, node network issues |
| **Error** | Container terminated with error (not looping) | Similar to CrashLoop but without retries (restartPolicy: Never) |
| **Evicted** | Pod was expelled from the node | Node out of disk, memory pressure on node |
| **OOMKilled** | Container exceeded memory limit | App with memory leak, limits too low for the workload |
| **CreateContainerConfigError** | Container configuration error | Referenced Secret or ConfigMap doesn't exist |

---

## YAML Structure Fundamentals

Understanding YAML structure is essential - not just copying templates, but knowing what each field means and why it's there.

### Base Structure for Any Kubernetes Resource

```yaml
apiVersion: v1                    # API version for this resource type
kind: Pod                         # Resource type (Pod, Deployment, Service, etc.)
metadata:                         # Information ABOUT the resource
  name: my-pod                    # Unique name within the namespace
  namespace: default              # Namespace where it lives (optional)
  labels:                         # Key-value pairs for organizing/selecting
    app: my-application
    environment: production
spec:                             # Specification - WHAT you want it to do
  # ... content specific to the "kind"
```

### Pod Anatomy

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:                     # List of containers (a pod can have multiple)
  - name: main-app                # Container name within the pod
    image: nginx:alpine           # Docker image to use
    command: ["nginx", "-g"]      # Command that overrides ENTRYPOINT
    ports:
    - containerPort: 80
```

> **Why is `containers` a list?**  
> A Pod can have multiple containers that share network and storage. This is used for sidecars (logging, proxies, etc.) - a very common pattern in service meshes like Istio.

### Deployment + Service Relationship

```yaml
apiVersion: apps/v1               # Deployments are in the "apps" API group
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 2                     # How many pod copies you want
  selector:                       # HOW the Deployment finds its pods
    matchLabels:
      app: backend
      version: v1
  template:                       # TEMPLATE for creating pods
    metadata:
      labels:                     # Labels the created pods will have
        app: backend
        version: v1
    spec:                         # Pod spec (same structure as above)
      containers:
      - name: nginx
        image: nginx:alpine
---                               # YAML document separator
apiVersion: v1
kind: Service
metadata:
  name: backend-svc
spec:
  selector:                       # HOW the Service finds pods to route traffic
    app: backend
    version: v1                   # Must match pod labels!
  ports:
  - port: 80
```

**Critical connection between Deployment and Service:**
- Deployment uses `selector.matchLabels` to know which pods belong to it
- Service uses `selector` to know which pods to send traffic to
- If labels don't match, the Service finds no endpoints

### Real-World Example: API Backend with Health Checks

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-api
  labels:
    app: user-api
    team: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-api
  template:
    metadata:
      labels:
        app: user-api
    spec:
      containers:
      - name: api
        image: my-registry.io/user-api:v2.1.0
        ports:
        - containerPort: 8000
        env:                              # Environment variables
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:                 # Reference to a Secret
              name: db-credentials
              key: connection-string
        - name: LOG_LEVEL
          value: "INFO"
        resources:                        # Resource limits
          requests:                       # Minimum guaranteed
            memory: "256Mi"
            cpu: "250m"
          limits:                         # Maximum allowed
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:                    # Is the container alive?
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 15
        readinessProbe:                   # Is it ready to receive traffic?
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
```

### CronJob Example (Scheduled Tasks)

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: db-backup
spec:
  schedule: "0 2 * * *"                   # Every day at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: my-registry.io/db-backup:latest
            env:
            - name: S3_BUCKET
              value: "backups-prod"
          restartPolicy: OnFailure
```

---

## The describe Command and Kubernetes Resources

The `kubectl describe` command works with any Kubernetes resource. The correct terminology is **resources** - everything in Kubernetes is a resource you can create, list, describe, modify, or delete.

### General Structure

```bash
kubectl describe <resource-type> <name>
```

### Common Resources for Troubleshooting

**Workloads:**
```bash
kubectl describe pod <name>           # Individual container
kubectl describe deployment <name>    # Manages pod replicas
kubectl describe statefulset <name>   # For stateful apps (DBs)
kubectl describe daemonset <name>     # One pod per node (monitoring agents)
kubectl describe job <name>           # Task that runs once
kubectl describe cronjob <name>       # Scheduled tasks
```

**Networking:**
```bash
kubectl describe service <name>       # Exposes pods (svc shortname)
kubectl describe ingress <name>       # External HTTP/HTTPS routing
kubectl describe endpoints <name>     # Actual IPs behind a Service
kubectl describe networkpolicy <name> # Firewall rules between pods
```

**Configuration and Secrets:**
```bash
kubectl describe configmap <name>     # Non-sensitive configuration
kubectl describe secret <name>        # Credentials, tokens, etc.
```

**Storage:**
```bash
kubectl describe pv <name>            # PersistentVolume (physical disk)
kubectl describe pvc <name>           # PersistentVolumeClaim (disk request)
kubectl describe storageclass <name>  # Available storage types
```

**Cluster and Nodes:**
```bash
kubectl describe node <name>          # Physical server/VM state
kubectl describe namespace <name>     # Isolated resource space
```

**Security and Access (RBAC):**
```bash
kubectl describe serviceaccount <name>      # Identity for pods
kubectl describe role <name>                # Permissions within namespace
kubectl describe clusterrole <name>         # Cluster-level permissions
kubectl describe rolebinding <name>         # Assigns role to user/sa
kubectl describe clusterrolebinding <name>  # Assigns clusterrole
```

### Useful Trick: List All Available Resources

```bash
kubectl api-resources
```

This shows all resources your cluster supports, including shortnames:

```
NAME                   SHORTNAMES   APIVERSION   NAMESPACED   KIND
pods                   po           v1           true         Pod
services               svc          v1           true         Service
deployments            deploy       apps/v1      true         Deployment
configmaps             cm           v1           true         ConfigMap
persistentvolumeclaims pvc          v1           true         PersistentVolumeClaim
```

### Most Relevant for Troubleshooting Interviews

| Resource | When to describe it | What you're looking for |
|----------|---------------------|-------------------------|
| **pod** | Container failing | Events, state, failure reason |
| **deployment** | Rollout not progressing | Conditions, available replicas |
| **service** | Broken connectivity | Selector, endpoints |
| **node** | Pods not scheduling | Conditions, available resources, taints |
| **pvc** | Storage issues | State (Bound/Pending), events |
| **ingress** | External traffic not arriving | Rules, backend service, events |

---

## Labels vs Namespaces: Understanding the Difference

This is a common point of confusion. The key insight is that labels are what enable dynamic relationships between resources - which is why a simple label mismatch can break service discovery.

### Fundamental Difference

| Aspect | Namespace | Labels |
|--------|-----------|--------|
| **Purpose** | Isolation and organization at cluster level | Identification and selection of resources |
| **Scope** | Hard barrier - resources DON'T see each other across namespaces | Flexible metadata - just informative tags |
| **Who uses it** | Kubernetes to separate resources | You (and other resources) to find/group |
| **Analogy** | Folders in a file system | Tags on photos or files |

### Namespace: Real Isolation

Think of namespaces as **departments in a company**. Each department has its own resources and doesn't see others by default.

```bash
# Resources in namespace "production" DON'T see resources in "development"
kubectl get pods -n production
kubectl get pods -n development
```

A pod in `namespace: production` cannot directly access a Service in `namespace: development` by name alone. It would need to use the FQDN:

```
my-service.development.svc.cluster.local
```

**Real use cases:**
- Separate environments: `dev`, `staging`, `production`
- Separate teams: `team-backend`, `team-frontend`
- Separate clients in multi-tenancy: `client-a`, `client-b`

### Labels: Flexible Metadata for Selection

Labels are just **key-value pairs** that you define. Kubernetes gives them no inherent meaning - you define the meaning.

```yaml
metadata:
  labels:
    app: user-api            # What application is it?
    environment: production  # What environment?
    team: backend            # What team maintains it?
    version: v2.1.0          # What version?
```

**The power is in selectors.** Other resources use labels to FIND related resources.

### How Selection Works (The Heart of the Matter)

The Service finds pods by labels, NOT by name:

```yaml
# Deployment creates pods with these labels
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    metadata:
      labels:
        app: backend       # ← Pods will have this label
        version: v1        # ← And this one

---
# Service looks for pods matching its selector
apiVersion: v1
kind: Service
spec:
  selector:
    app: backend           # ← Looks for pods with app=backend
    version: v2            # ← And version=v2... THEY DON'T EXIST!
```

The Service performs a query like: *"Give me all pods where `app=backend` AND `version=v2`"*

Since there are no pods with `version: v2`, the result is empty = no endpoints.

### Practical Verification

```bash
# See what labels pods have
kubectl get pods --show-labels

# Simulate the Service's query
kubectl get pods -l app=backend,version=v1    # Finds pods
kubectl get pods -l app=backend,version=v2    # Finds nothing

# See the endpoints (pod IPs that the Service found)
kubectl get endpoints backend-svc
```

### Who Uses Labels to Select What

| Resource | Uses selector to find |
|----------|----------------------|
| **Service** | Pods to send traffic to |
| **Deployment** | Pods that belong to it (to know how many exist) |
| **ReplicaSet** | Pods it must maintain |
| **NetworkPolicy** | Pods to apply network rules to |
| **PodDisruptionBudget** | Pods to protect during maintenance |
| **Horizontal Pod Autoscaler** | Deployment/pods to scale |

### Helpful Analogy

**Namespace** = Office building
- Each floor is a different namespace
- Resources on floor 3 don't see resources on floor 5
- You have to specifically go to that floor to access them

**Labels** = Employee badges
- Each person has a badge with: department, role, project
- You can search: "all Marketing people working on Project-X"
- Badges don't create barriers, they just allow identification and grouping

### Common Label Conventions

Kubernetes recommends these conventions:

```yaml
labels:
  # App identification
  app.kubernetes.io/name: user-api
  app.kubernetes.io/instance: user-api-prod
  app.kubernetes.io/version: "2.1.0"
  app.kubernetes.io/component: backend
  app.kubernetes.io/part-of: sales-system
  
  # Custom organization labels
  team: backend
  cost-center: engineering
  environment: production
```

In practice, many teams simplify:

```yaml
labels:
  app: user-api
  env: prod
  version: v2
```

---

## Quick Reference: Troubleshooting Framework

For any Kubernetes issue, follow this structure:

1. **IMPACT**: What's affected? Is the service degraded?
2. **DIAGNOSIS**: What commands reveal the root cause?
3. **RESOLUTION**: How do you fix it?
4. **PREVENTION**: How do you prevent it from happening again?

### Example: Pod in CrashLoopBackOff

| Step | Action |
|------|--------|
| **IMPACT** | Service may be degraded, pod not serving traffic |
| **DIAGNOSIS** | `kubectl describe pod` for events, `kubectl logs --previous` for crash reason |
| **RESOLUTION** | Fix based on root cause (bad command, missing config, OOMKilled) |
| **PREVENTION** | Add proper health checks, resource limits, CI validation |

### Example: Service Has No Endpoints

| Step | Action |
|------|--------|
| **IMPACT** | No traffic reaching pods |
| **DIAGNOSIS** | Compare service selector with pod labels: `kubectl describe svc`, `kubectl get pods --show-labels` |
| **RESOLUTION** | Fix label mismatch |
| **PREVENTION** | Use consistent labeling conventions, CI validation |

---

## Summary

Understanding Kubernetes troubleshooting requires knowing:

1. **What error states mean** - not just their names, but the underlying causes
2. **How YAML structures work** - the relationship between spec fields and runtime behavior
3. **What resources exist** - and how to inspect them with `describe`
4. **How labels enable dynamic relationships** - the selection mechanism that connects Services to Pods

This foundation enables systematic debugging rather than guesswork.