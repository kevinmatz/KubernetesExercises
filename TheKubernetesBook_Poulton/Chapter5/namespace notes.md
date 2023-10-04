# Notes on Kubernetes namespaces

- Namespaces in Kubernetes can be used to divide up resources within a cluster -- to create a *virtual cluster*.
- Resource quotas and policies can be applied to a namespace / virtual cluster.
- Each namespace can also have its own users and RBAC rules/permissions, and accounting can be done by namespace.
- Namespaces are not intended as a "strong workload isolation boundary" or as a way to "isolate hostile workloads". You wouldn't want to use namespaces as a way to have different competing customers/clients/tenants in the same cluster (multitenancy), as those resources could "see" each other and a malicious resource could access the other ones.
- Pre-created namespaces are:
  - `default`: if you create resources without specifying a namespace, they go here
  - `kube-system`: control-plane components run here
  - `kube-public`: a namespace for any objects that need to be readable by everyone
  - `kube-node-lease`: for node heartbeat and managing node leases
- `kubectl describe namespace <namespace>` (or use `ns` for an abbreviation for `namespace`)
  - Shows details about a namespace
- `kubectl get services --namespace kube-system`
  - Filters by namespace (`-n` is an abbreviation for `--namespace`)
- A namespace needs to be declared and applied before resources can be deployed into that namespace.
  - One way to declare a namespace is:
    - `kubectl create namespace hydra`
  - Or, you can create a YAML manifest file with `kind: Namespace` to define a namespace, then use `kubectl apply -f <filename>` to apply it
- `kubectl delete namespace hydra`
  - Deletes the namespace `hydra`
- You can use `-n <namespace>` or `--namspace <namespace>` with all kubectl commands, or, you can set your *kubeconfig* to automatically work with a specific namespace
  - Example: `kubectl config set-context --current --namespace shield`
- Two ways to deploy resources into a namespace:
  - "Imperatively"
    - Add the `-n` or `--namespace` option to kubectl commands
  - "Declaratively"
    - In the YAML manifest files, specify the namespace in the `metadata:` section:

```
apiVersion: v1
kind: Service
metadata:
  namespace: shield
  name: the-bus
(etc.)
```

