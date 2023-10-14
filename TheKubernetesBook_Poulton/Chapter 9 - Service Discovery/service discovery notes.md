# Notes on Kubernetes Service Discovery

- Services provide a stable DNS hostname, (virtual) IP address, and port for a Deployment of Pods, but how do other Pods in the cluster find the Service to know the hostname/IP/port?
- Kubernetes provides a **service registry**; Services *register* with it, and then the registry allows *discovery* so other apps can find and consume the Service
- Any time a Service is created, it is automatically added to the service registry

- Kubernetes operates a well-known internal DNS service as the service registry; this internal DNS service is called the **cluster DNS** and it is based on CoreDNS
- Every Pod in the cluster is automatically configured to know where to find it
- The cluster DNS lives in the Namespace `kube-system`, is managed as a Deployment named `coredns`, and is fronted by a Service `kube-dns`
  - `kubectl get pods -n kube-system -l 8s-app=kube-dns`
  - `kubectl get deploy -n kube-system -l k8s-app=kube-dns`
  - `kubectl get svc -n kube-system -l k8s-app=kube-dns`

- Service registration steps:
  1. Post a Service manifest to API server
  2. Request is authenticated, authorized, subjected to policies, etc.
  3. Service is allocated a stable virtual IP address called the **ClusterIP**
  4. EndpointSlice objects are created to track the healthy Pods matching the Service's selection criteria (labels)
  5. The Pod network is configured to handle traffic sent to the ClusterIP
  6. The mapping between the Service's name and its ClusterIP is added to the cluster DNS

- Namespaces and service discovery
  - Apps need to know the service names of the services (apps) they are trying to communicate with
  - Can have a "dev" and "prod" namespace, both with a Service with the same name in them
  - An application with a Service called "ent" (for "enterprise") in the "dev" namespace can be accessed from within the "dev" namespace as simply "ent"
    - e.g., from the command line in a container in a Pod in that namespace, can do `curl ent:8080`
  - From outside of the namespace, have to fully-qualify it as: `ent.dev.svc.cluster.local`, like this: `curl ent.dev.svc.cluster.local:8080`

- Book has much technical detail on how the resolution works
  - Kubernetes automatically sets up each container with a customized `/etc/resolv.conf` file that makes DNS lookups use the cluster DNS service
  - "ClusterIPs are on a 'special' network called the *service network*, and there are no routes to it! This means containers send all ClusterIP traffic to their *default gateway*." ...which sends traffic to the node it is running on, and since that node also doesn't have a route to the service network, it also sends it to its own default gateway. Kubernetes (whenever new Service or EndpointSlice objects are created) sets up IPVS rules that tell the node to intercept traffic targeted at the ClusterIP, and redirect it to individual Pod IPs.
  - In other words, traffic headed for an address on the service network lands in a "trap", and the traffic gets redirected to a healthy Pod's IP (that matches the Service's selector)

- Example from book: `kubectl apply -f sd-example.yml` with "dev" and "prod" namespaces
  - Connect to the "jump" Pod in the "dev" namespace: `kubectl exec -it jump --namespace dev -- bash`
  - `cat /etc/resolv.conf` to verify the search domains:
    - `search dev.svc.cluster.local svc.cluster.local cluster.local`
  - Install curl (the "jump" Pod is a base Ubuntu container): `apt-get update && apt-get install curl -y`
  - `curl ent:8080`
    - shows a message from one of the two Pods under the "ent" Service in the "dev" namespace
  - `curl ent.prod.svc.cluster.local:8080`
    - shows a message from one of the two Pods under the "ent" Service in the "prod" namespace
  - `exit`

- See book for details notes on troubleshooting



