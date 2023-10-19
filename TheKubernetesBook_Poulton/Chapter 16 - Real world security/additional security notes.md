# Notes on Kubernetes security

- CI/CD security practices checklist 
  1. Configure your environment to only pull and run container images that have been signed
  2. Configure network rules to control which notes can push and pull images
  3. Configure container image repositories with RBAC rules
  4. Developers should build app containers based on approved base images
    - Base layer (e.g., Alpine Linux), libraries/dependencies layer (e.g., NGINX or MongoDB), then app code as the third layer
  5. Developers should sign container images and push to approved repos
  6. Container images must be scanned for known vulnerabilities and quarantined if the scan detects issues (then need a review process to see if any issues are false positives)
  7. Security team should review source code and scan results, and container and Pod configuration files
  8. Security team should sign the image before it goes into production
  9. Pull and run operations should verify image signatures

- Infrastructure and networking
  - Cluster-level workload isolation
    - Kubernetes does not support secure multi-tenant clusters; Namespaces are just a convenient way to group resources and applying policies; they don't create any security boundaries
    - So "competing" workloads should always be run on separate clusters
  - Node isolation
    - If some Pods/applications require elevated privileges like root access, you may wish to isolate ("ring-fence") these on a subset of worker nodes; use labels, affinity rules, and "taints" to target workloads to specific nodes
  - Runtime isolation
    - Containers on the same node share a single kernel; never meant as strong security barriers; virtual machines are more strongly isolated
  - Network isolation
    - Firewalls allow rules that allow or deny traffic
    - In Kubernetes, Pods communicate with each other over the **pod network**, but Kubernetes doesn't implement it, but offers a plugin model, Container Network Interface (CNI). CNI vendors implement the pod network. Two types:
      - Overlay (a "virtual network"/overlay can span multiple subnets but this means traffic must be encapsulated in order to pass to another subnet which can be problematic for firewalls that do deep packet inspection)
      - Border Gateway Protocol (BGP) (routing that uses peers to determine routes and does not encapsulate traffic and don't obscure source and destination addresses)
    - Combination of physical and software (host-based) firewalls can be most secure
  - Identity and Access Management (IAM)
    - RBAC, covered in previous chapters
    - Remote SSH access to cluster nodes should only be permitted for node management activities that can't be done via Kubernetes API, "break-the-glass" emergencies when the API server is down, and troubleshooting
    - Multi-Factor Authentication for accounts with admin access and root access to cluster nodes
  - Auditing and security monitoring
    - Center for Information Security (CIS) has established benchmarks for Kubernetes security
    - Aquasec has created `kube-bench` tool to implement CIS tests; run it against each node, typically as part of provisioning
      - Can also be used for before and after analysis after a breach
    - When Pods terminate, if they stored logs locally, those logs disappear, so log centralization is desirable
    - Log actions done by SSH sessions to control plane and worker nodes
    - Managing centralized logs needs specialized tools for managing the sheer amount of data
    - SELinux (secure Linux) policies


