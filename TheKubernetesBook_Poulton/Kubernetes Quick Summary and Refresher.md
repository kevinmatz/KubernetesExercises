# Quick summary/refresher of Kubernetes concepts

* Container orchestration system
  * Lets you deploy a cluster to different cloud service providers; mostly platform-independent but storage, load balancers, etc. depend on the cloud provider
  * Suitable for cloud-native apps composed of microservices
* Abbreviated as K8s

*Notes on key concepts from [The Kubernetes Book, 2023 Edition](https://www.amazon.com/Kubernetes-Book-Nigel-Poulton/dp/1916585000) by Nigel Poulton:*

* Declarative using YAML **manifest** files
  * Post manifest files to the API server using commands such as:
    * `kubectl apply -f my_declarative_file.yml`
    * Kubernetes then makes changes to the cluster to reconcile the as-is (observed) state with the to-be (desired) state
    * All requests through kubectl command or the API are subject to authorization and authentication
* **Nodes** are the worker machines (virtual machines or physical servers)
* A **Pod** is the smallest deployable unit
  * One Pod runs on one Node
  * A Pod contains one or more containers
    * Containers are usually Docker containers but other runtimes like `containerd` are supported
* A **Cluster** consists of one or more worker Nodes, where each Node may host a Pod
  * A Cluster also has a control plane (master Nodes although “master” terminology is no longer used) that monitor and manage the state of the cluster and the scheduling of Pods, perform self-healing, and expose the API
* Resources can be organized under **Namespaces**
  * Namespaces can have their own policies (e.g., resource quotas), users, and RBAC permissions
  * Accounting can be done by Namespace
  * Namespaces are not intended as a mechanism for strong isolation of "hostile" workloads
* A **Deployment** is a set of replicas of a Pod template (Deployments use ReplicaSets to manage the Pods; it’s best not to access ReplicaSets directly)
  * Specify number of Pod replicas, what container image(s) to use for the container(s) in the Pod, what network ports to expose, and what strategy and settings to use to perform rolling updates
* **Scaling**
  * Update and post YAML manifest with a changed number of replicas; Pods get created or destroyed in order to match the desired state
  * Various settings on how long replicas must be up and stable before doing the next one, etc.
* **Rollouts / rolling updates / releases**
  * New container image(s)
  * Kubernetes updates Pods by terminating then and replacing them with new Pods with the new container image(s)
* **Rollbacks**
  * Kubernetes keeps a history of rollouts; can roll out a previous image (rollback is done as a rollout of the previous image)
* **Services** provide a stable IP address, DNS name, and port as a reliable endpoint for accessing a set of Pods
  * **NodePort** services – if an external client access a dedicated port on any cluster Node, it gets redirected to the Service node which selects a Node and redirects to it (using the targetPort)
  * **LoadBalancer** service – if deployed on cloud provider, allows external clients to access dedicated port on cloud provider’s load balancer, which distributes traffic amongst the Pods matching the selection criteria
* A **Service Registry** (an internal **cluster DNS** service named `kube-dns``) is provided by Kubernetes
  * All services are registered with it and assigned a stable virtual IP (**ClusterIP**), and the mapping between the service name and ClusterIP is added to the cluster DNS
  * Every Pod is automatically configured to know where to find it
  * Pods can just access the service name (e.g., `curl myservice:8000`)  and through a complex resolution mechanism, it will work and the service will redirect the request to one of the Pods in the Deployment managed by the Service
* Cloud platform load balancers are not cheap, so **Ingress** objects let you expose multiple web applications through a single load balancer, using routing rules (subdomains or paths in the URL are used to decide which service to route to)
* **Storage:** Kubernetes supports cloud storage back-ends
  * A plugin (**provisioner**) based on the Container Storage Interface (CSI) is required for each type of storage resource
  * **PersistentVolume (PV)** maps to an external storage asset and is the access point for the volume
  * **PersistentVolumeClaim (PVC)** are like authorization tickets that Pods need to claim to access PVs
  * **StorageClasses (CS)** automate some of the steps
* Various policies (`ReadOnly`, `ReadWriteOnce` for access by one PVC, `ReadWriteMany` can be bound by multiple PVCs/Pods); `ReclaimPolicy` (delete or retain volume when PVC is released)
* **ConfigMaps** and **Secrets** are key-value map dictionaries that hold configuration info
  * Can inject into environment variables, or can be accessed as files in a mounted volume, or apps can access the Kubernetes API to read values
  * Secrets are intended for API keys, passwords, certificates, tokens, etc., but out of the box, Kubernetes does not encrypt secrets at rest or over the network
    * Can use third-party plugins/tools like HashiCorp Vault for better security
* **StatefulSets** (**`sts`**) are a form of Deployment for operating applications that persist data in a database or other data store that is running on (a) Pod(s) on Kubernetes
  * Guarantees persistent pod names, DNS hostnames, and volume bindings to storage for a Pod (these attributes are the Pod’s “state” or “sticky ID”)
  * StatefulSets ensure that the sticky ID attributes are persisted predictably even when the Pod fails and is restarted or if the Pod is scaled/replicated
* **API security and RBAC**
  * For requests:
    * Authentication module (authN) checks if user is who they claim to be
      * Kubernetes does not have an identity database; you have to provide a third-party external one such as Active Directory (AD), IAM, client certificates, webhooks, etc.
    * Authorization module (authZ) checks whether user has permission to do the requested action
      * “Least-privilege deny-by-default” so need to explicitly grant all needed permissions
    * Admission control then checks/applies further policies
* **Security**
  * Complicated, hire an expert!
