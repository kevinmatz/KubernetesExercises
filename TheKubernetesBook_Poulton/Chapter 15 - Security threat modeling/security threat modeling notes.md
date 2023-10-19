# Notes on Kubernetes Security: Threat Modeling

- STRIDE model of categories of potential security threats:
  1. **Spoofing**
    - Spoofing: an actor pretending to be somebody else in order to gain extra privileges on a system
    - Authentication with mTLS (mutual TLS):
      - Built-in auto-generated Certificate Authority (CA) not adequate for production systems
      - Generally need two CAs, one for authenticating internal systems, and a third-party one for authenticating external systems
    - Pod-to-pod/app-to-app communications:
      - Pods could spoof another
      - Can mount certificates into Pods to authenticate Pod identity
      - Set `automountServiceAuthenticationToken: False` on Pods that don't need to access the API server; more attributes available but little detail provided
  2. **Tampering**
    - Tampering: the act of changing something, maliciously (e.g., to cause denial of service or elevation of privileges in order to do further harmful acts)
    - TLS helps prevent in-transit tampering
    - At rest, config files, container images, Kubernetes binaries, container runtime binaries could all be tampered with
    - Restrict access to repos containing config files
    - Only do remote bootstrapping over SSH
    - Check checksums on all downloads
    - Restrict access to container image registry
    - Auditing and alerting for access to and changes to config files and binaries (Linux provides an audit daemon `auditctl`)
    - Can set a container's filesystem to read-only
  3. **Repudiation**
    - Repudiation: creating doubt about something
    - Non-repudiation: providing proof about something; proving that specific actions were carried out by specific actors
    - Can enable Kubernetes API server audit logging
    - Should also audit network firewalls, container runtimes, nodes (kubelets), and your applications in the Pods
    - Use a `DaemonSet` (not in the scope of the book) to deploy an agent to all nodes to collect logs and send them to a centralized secure location
    - Use audit daemon `auditctl` to audit changes to binaries and config files
  4. **Information disclosure**
    - Information disclosure: unwanted exposure or leaking of sensitive data
    - Limit and audit access to the cluster store (`etcd` database), the prime target for information disclosure attacks
    - Use Secrets instead of ConfigMaps for sensitive data, but beware of limitations
    - Encryption of secrets not enabled by default; even when enabled there are weaknesses (data encryption key stored on same node as the Secret)
    - This part of Kubernetes is changing rapidly; look into Key Encryption Keys (KEK), Hardware Security Modules (HSM), cloud-based Key Management Stores (KMS)
  5. **Denial of service**
    - Denial of service: making a system unavailable, e.g., by overloading it with requests
    - Ensure control plane services are set up for High Availability (HA) using multiple nodes, and consider having the nodes spread across multiple availability zones so that a DOS attack on one network doesn't take down all the control plane nodes
    - Spread worker nodes across multiple availability zones
    - Configure limits for memory, CPU, storage, Kubernetes objects (Pods, ReplicaSets, Services, etc.) to prevent resource starvation and spiraling cloud platform costs
    - Restrict number of processes a Pod can create with `podPidsLimit` (to prevent a "fork bomb" attack)
    - Set up monitoring, alerting, firewalls, etc. for the API server (REST API over TCP socket is prime target for botnet DOS attacks)
    - Isolate `etcd` cluster store at the network level so that only control plane notes can contact it
      - Consider a separate cluster for `etcd` (rather than having it as part of the control plane) for extremely large applications
      - Test `etcd` cluster performance as it can easily become the bottleneck
    - Configure Pod resource request limits and Kubernetes Access Policies for pod-to-pod communication
    - Set up application-level authorization policies and/or API token-based authentication
  6. **Elevation of privilege**
    - Privilege escalation: an actor gains access privileges higher than what was granted
    - Properly configure RBAC for users for authorization and authentication
    - Configure Node authorization for API requests made by Nodes
    - Webhook mode lets you use a third-party RBAC engine but this can become a bottleneck and single point of failure
    - Force containers to use non-root users (UID configuration, `runAsUser` settings in `securityContext`, and maintain a map of UID usage -- but this is considered clunky)
    - Use User Namespaces when a container must run something as root
    - "Capability dropping": can configure exactly which Linux capabilities, like setting the system clock, are permitted; extremely granular and finicky, needs extensive testing
    - Can configure which Linux system calls (syscalls) are permitted or blocked/filtered (see `seccomp` in Kubernetes since 1.19)
    - Prevent privilege escalation of child processes in Linux using `allowPrivilegeEscalation: false`
    - Pod security:
      - Pod Security Policies (PSP) was removed in Kubernetes v1.25 due to complexity and flaws
      - Pod Security Standards (PSS), new in v1.25
        - Privileged (very permissive), Baseline (sensible defaults), and Restricted (gold-standard) policies that are set by the community and can't be changed but can apparently be applied to your whole cluster
      - Pod Security Admission (PSA), new in v1.25
        - Works as a validating admissions controller for enforcing PSS policies re: creating Pods
        - Modes: Warn (warns user but allows violating Pods), Audit (audit logs event but allows violating Pods), Enforce (prohibits violating Pods from being created)
        - Configurable at Namespace level
      - Third-party solutions available if PSS and PSA not adequate
    - Watch Kubernetes community's feed of CVE's (vulnerabilities)

- This chapter does a very broad survey of dozens of mechanisms, techniques, and best practices, but is also not in any way complete, and each is not presented with enough detail
- For a production system, it's likely best to hire an expert to review, configure, monitor security for a Kubernetes cluster

- Follow-up reading:
  - Cloud Native Security Whitepaper
