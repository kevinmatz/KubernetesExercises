# Notes on Kubernetes API security and Role-Based Access Control

- What/who can make CRUD-style requests to the API server?
  - Admins/operators/developers, using `kubectl`
  - Pods
  - Kubelets
  - Control plane services

- If using a `kubectl apply` command, the connection between the client and the API server is secure due to **TLS**
- Then the **authentication module (authN)** determines if the user is who they claim to be
- Then the **authorization module (authZ)** determines whether this user has permission to do the requested action (e.g., to create a Deployment in a specific Namespace)
- If that check passes, then finally **admission control** checks and applies policies, and the request is finally accepted and executed

- **Authentication (authN)**
  - All requests to the API server must include credentials, which the authentication layer verifies
  - If verification fials, an `HTTP 401 Unauthorized` is returned
  - Kubernetes does not have an identity database; you have to use an external system
  - Options include Active Directory (AD) integration, Identity Access Management (IAM) integration, client certificates, webhooks, etc.
  - Most clusters support client certificates out of the box but for real production use you should use your corporate identity management system
  - `kubeconfig` file
    - Lives under:
      - `/home/<user>/.kube/config on Linux`
      - `C:\Users\<user>\.kube\config on Windows`
    - Contains sections:
      - `clusters`
        - friendly name, API server endpoint, public key of certificate authority (CA)
      - `users`
        - name and client certificate
      - `contexts`
        - combines users and clusters
      - `current-context`
        - indicates the cluster and user that `kubectl` will use for all commands
  - The user from `current-context` will be authenticated by Kubernetes (it will pass it to the third-party authentication module), or, if client certificates are being used, it will determine if the certificate is signed by a trusted CA

- **Authorization (authZ) - Role-Based Access Control (RBAC)**
  - Kubernetes authorization is also pluggable; you can run multiple authZ modules on a single cluster
  - As soon as any one module authorizes a request, it goes on to the next stage, admissions control

- RBAC: which **users** can perform which **actions** against which **resources**
  - e.g., user Bob can create Pods
- RBAC in Kubernetes is "least-privilege deny-by-default" system, so you need to enable specific actions via **allow rules** (there are no **deny rules**)

- **Roles** define a set of permissions. This example defailt are role `read-deployments` that grants permission to `get`, `watch`, and `list` objects of type `Deployment` in the `shield` Namespace:

```
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: shield
  name: read-deployments
rules:
- apiGroups: ["apps"]     
  resources: ["deployments"]
  verbs: ["get", "watch", "list"]
```

- A role definition always applies to a single specified Namespace
- `apiGroups` and `resources` define the object
  - To see all resources supported on your cluster, and the `apiGroup` for each, run:
    - `kubectl api-resources --sort-by name -o wide`
- `verbs` define the actions
  - `create` = POST
  - `get`, `list`, `watch` = GET
  - `update` = PUT
  - `patch` = PATCH
  - `delete` = DELETE
- Full documentation: [https://kubernetes.io/docs/reference/access-authn-authz/rbac/](https://kubernetes.io/docs/reference/access-authn-authz/rbac/)

- **RoleBindings** bind a Role to users. This example grants the `read-deployments` role to a user called `sky`:

```
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-deployments
  namespace: shield
subjects:
- kind: User
  name: sky
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: read-deployments
  apiGroup: rbac.authorization.k8s.io
```

- If both of the above are deployed to a cluster, an authenticated user `sky` will be able to run commands like `kubectl get deployments -n shield`

- An asterisk can be used as a wildcard:

```
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
```

- `Role` and `RoleBinding` are used for single namespaces
- Use `ClusterRole` and `ClusterRoleBinding` for rules that apply to all  namespaces
  - You can use `ClusterRole` to define common roles at the cluster level, and then use `RoleBinding` to bind them to specific Namespaces


- **Admission control**
  - This runs after authentication and authorization
  - Enforces policies, but only for requests that will modify state (read operations are not subject to admission control)
  - Short circuit evaluation: as soon as one admission controller rejects a request, no other admission controllers are evaluated
  - Two types of admission controllers:
    1. **mutating**: these check for policy compliance and can modify requests; these always run first
    2. **validating**: these check for policy compliance but cannot modify requests
  - Example: all new and update objects must have label `env=prod`
    - a mutating controller can check for the label and add it if it doesn't exist
    - a validating controller can only check the label and reject it if it doesn't exist
  - `AlwaysPullImages` mutating controller sets `spec.containers.imagePullPolicy=Always` for all new Pods, forcing container images to always be pulled from the registry
  - Book doesn't provide any details on how to set these up
