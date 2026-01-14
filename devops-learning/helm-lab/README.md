# My First Helm Lab

A hands-on beginner's guide to Kubernetes package management using Helm.

## What You'll Learn

- What problem Helm solves
- How to use existing charts from repositories
- The Helm workflow: install → upgrade → rollback → uninstall
- How to create your own Helm chart
- Customizing deployments with values

## Prerequisites

- Kubernetes cluster (minikube, kind, or cloud-based)
- kubectl configured and connected
- Helm installed

### Installing Helm

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
helm version
```

### Verify Cluster Connection

```bash
kubectl get nodes
```

## What Problem Does Helm Solve?

A typical Kubernetes application requires multiple YAML files:

```
deployment.yaml
service.yaml
configmap.yaml
secret.yaml
ingress.yaml
```

If you have 3 environments (dev, staging, prod), do you copy-paste everything and manually change values?

**Helm is a package manager for Kubernetes.** It allows you to:

1. **Package** all those YAMLs into a "chart"
2. **Parameterize** values (name, replicas, image, etc.)
3. **Install/upgrade/rollback** applications with a single command

### The Analogy

> "Helm is to Kubernetes what apt/yum is to Linux, or npm to Node.js. Instead of installing system packages or libraries, you install complete applications into a cluster."

## The Helm Workflow

```bash
helm repo add <name> <url>    # Add a chart repository
helm search repo <keyword>    # Search for charts
helm install <release> <chart> # Install a chart
helm upgrade <release> <chart> # Update a release
helm rollback <release> <rev>  # Rollback to previous revision
helm uninstall <release>       # Remove a release
helm list                      # List installed releases
```

## Hands-On: Using Existing Charts

### Step 1: Add a Repository

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

### Step 2: Search for Charts

```bash
helm search repo nginx
```

### Step 3: Install a Chart

```bash
helm install mi-nginx bitnami/nginx
```

Where:
- `mi-nginx` = release name (your instance)
- `bitnami/nginx` = the chart to install

### Step 4: Verify Installation

```bash
helm list
kubectl get pods
kubectl get svc
```

### Step 5: Customize with Values

```bash
helm upgrade mi-nginx bitnami/nginx --set replicaCount=3
kubectl get pods  # Should show 3 pods now
```

### Step 6: Rollback

```bash
helm rollback mi-nginx 1
kubectl get pods  # Back to 1 pod
```

### Step 7: View History

```bash
helm history mi-nginx
```

### Step 8: Cleanup

```bash
helm uninstall mi-nginx
```

## Hands-On: Creating Your Own Chart

### Step 1: Generate Chart Structure

```bash
helm create my-app
```

### Step 2: Explore the Structure

```
my-app/
├── Chart.yaml      # Chart metadata (name, version, description)
├── values.yaml     # Default values users can override
├── templates/      # Kubernetes YAMLs with template variables
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── ...
└── charts/         # Dependencies (other charts)
```

### Step 3: Understanding Templates

Templates use Go templating. Example from `deployment.yaml`:

```yaml
replicas: {{ .Values.replicaCount }}
```

Helm replaces `{{ .Values.replicaCount }}` with the value from `values.yaml` or `--set` flags.

### Step 4: Install Your Chart

```bash
helm install test-release ./my-app
kubectl get pods
kubectl get svc
```

### Step 5: Customize and Upgrade

```bash
helm upgrade test-release ./my-app --set replicaCount=2
kubectl get pods  # Should show 2 pods
```

### Step 6: Cleanup

```bash
helm uninstall test-release
```

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Chart** | A package containing Kubernetes resource templates |
| **Release** | An instance of a chart running in a cluster |
| **Repository** | A collection of charts (like npm registry) |
| **Values** | Configuration that customizes a chart |
| **Revision** | A version of a release (increments on each upgrade) |

## Common Interview Questions

**Q: What is Helm and why use it?**

A: Helm is a package manager for Kubernetes. It allows you to package applications as charts, which are templates of Kubernetes resources with configurable values. Instead of maintaining multiple YAMLs per environment, you define one chart and change values for dev, staging, and prod. It also maintains release history, enabling rollbacks if a deployment fails.

**Q: What's the difference between `helm install` and `helm upgrade`?**

A: Install creates a new release. Upgrade modifies an existing release. In practice, `helm upgrade --install` is commonly used because it does both: installs if the release doesn't exist, upgrades if it does.

**Q: What is a Helm chart?**

A: A chart is a collection of files that describe a set of Kubernetes resources. It contains templates (Kubernetes YAMLs with variables), a values file (default configuration), and metadata. Charts can be versioned, shared, and reused across teams and environments.

**Q: How do you customize a Helm deployment?**

A: Three ways: (1) Edit `values.yaml` directly, (2) Pass a custom values file with `-f custom-values.yaml`, or (3) Override specific values with `--set key=value`. The precedence is: `--set` > `-f file` > default `values.yaml`.

**Q: How does Helm handle rollbacks?**

A: Helm maintains a history of all releases. Each upgrade increments the revision number. You can rollback to any previous revision with `helm rollback <release> <revision>`. Helm stores release history in Kubernetes secrets by default.

## Useful Commands Reference

```bash
# Repository management
helm repo add <name> <url>
helm repo update
helm repo list
helm search repo <keyword>

# Release management  
helm install <release> <chart>
helm upgrade <release> <chart>
helm upgrade --install <release> <chart>  # Install or upgrade
helm rollback <release> <revision>
helm uninstall <release>

# Information
helm list
helm status <release>
helm history <release>
helm show values <chart>

# Debugging
helm template <release> <chart>  # Render templates locally
helm install --dry-run --debug <release> <chart>  # Test without installing
```

## Next Steps

- [ ] Create a chart for your own application
- [ ] Use values files for different environments (dev, staging, prod)
- [ ] Explore Helm hooks for lifecycle management
- [ ] Learn about chart dependencies
- [ ] Integrate Helm with CI/CD pipelines

## Resources

- [Helm Documentation](https://helm.sh/docs/)
- [Artifact Hub](https://artifacthub.io/) - Public chart repository
- [Chart Development Guide](https://helm.sh/docs/chart_template_guide/)