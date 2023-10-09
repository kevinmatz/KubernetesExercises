# Notes on Kubernetes Ingress

- Ingress lets you expose multiple ClusterIP Services (multiple web applications) through a single load balancer on the cloud platform
  - Rationale: Load balancers on cloud platforms are not cheap, and if you have 20 internet-facing apps, you don't want 20 load balancers
    - And note that NodePorts only work on ports 30000..32767 "and require knowledge of node names or IPs"
  - You configure rules governing how traffic reaching the load balancer is routed to backend Services

- There is some overlap between Ingress and service meshes; if you use a service mesh, you may not need Ingress

- Some Kubernetes clusters don't ship with a built-in Ingress controller, so you have to install your own

- Ingress operates at OSI layer 7 (application layer) so it can inspect HTTP headers and forward based on hostnames and paths

- Host-based routing:
  - Example: shield.mcu.com routes to svc-shield
  - DNS names need to point to the public endpoint of the Ingress load balancer (e.g., shield.mcu.com and hydra.mcu.com needs to resolve to the public IP of the Ingress load-balancer)
- Path-based routing:
  - Example: mcu.com/shield routes to svc-shield

- Host-based routing:
  - access via shield.mcu.com --> LoadBalancer Service --> Ingress (routing rules) --> svc-shield

- You may want to run multiple Ingress controllers on a single cluster, in which case:
  - You create an **IngressClass** and when creating an Ingress, you assign it to an IngressClass

- Example of creating an IngressClass:

```
apiVersion: networking.k8s.io/v1
kind: IngressClass
metadata:
  name: igc-nginx
spec:
  controller: nginx.org/ingress-controller
```

- Then in the Ingress manifest YML file, you reference the class without the `igc-` prefix:

```
...
spec:
  ingressClassName: nginx
...
```

- Examples from the book need to be run on an actual cloud platform (not Docker Desktop) and you may need to install an appropriate controller such as the NGINX Ingress Controller
  - To check whether your cluster has a built-in Ingress controller, run `kubectl get ingress`

- Installing NGINX Ingress Controller:
  - `kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.5.1/deploy/static/provider/cloud/deploy.yaml`
  - `kubectl get pods -n ingress-nginx -l app.kubernetes.io/name=ingress-nginx`
  - `kubectl get ingressclass` --> `nginx` IngressClass exists
  - `kubectl describe ingressclass nginx`

- Example in book shows how to configure routing for:

```
shield.mcu.com
hydra.mcu.com
mcu.com/shield
mcu.com/hydra
mcu.com --> no routing (intentionally)
```

- DNS then needs to be configured to point hostnames to the Ingress load balancers's public IP
  - Use `kubectl get ingress` to determine the public IP of the Ingress
- To test locally (even with the cluster running on a cloud platform), edit the `/etc/hosts` file (`C:\Windows\System32\drivers\etc\hosts` on Windows) and add entries that point the above domains/subdomains to the public IP of the Ingress:

```
34.159.139.255  shield.mcu.com
34.159.139.255  hydra.mcu.com
34.159.139.255  mcu.com
```

- Then visiting `shield.mcu.com`, `hydra.mcu.com`, `mcu.com/shield`, `mcu.com/hydra` on the local machine routes to/through the Ingress load balancer
- A request for `mcu.com` is routed to the "default backend" as there is no ingress rule configured; the error message will vary but will typically be some form of a "response 404", "service rules nonexistent"
- When finished testing, be sure to remove the entries from the hosts file

- Don't leave the example running as the load balancer and cluster will incur costs!
  - `kubectl delete ingress mcu-all`
  - `kubectl delete -f app.yml`

- If you want to delete the NGINX Ingress controller, do:
  - `kubectl delete namespace ingress-nginx`
  - `kubectl delete clusterrole ingress-nginx`
  - `kubectl delete clusterrolebinding ingress-nginx`
