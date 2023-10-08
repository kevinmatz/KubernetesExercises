# Notes on Kubernetes Services

- As Pods go up and down, there is constant IP churn as each new Pod is assigned a new IP
- Services provide a stable IP address, DNS name, and port, so that there is a reliable endpoint for accessing a set of Pods that match selection criteria (e.g., matching by label)
- Services provide load-balancing across the Pods

- Implementation detail: Services maintain a list of `EndpointSlice` objects corresponding to healthy Pods
  - Note: older versions of Kubernetes used `Endpoint` objects
  - `kubectl get endpointslices`, `kubectl describe endpointslice <name>`

- **NodePort** Services allow external clients to access a dedicated port on any cluster node (Pod), and it redirects as follows:
  - If an external client accesses port 30050 on a node, it is redirected to the Service node, which then uses the EndpointSlices to select a Pod and redirects to it (using the `targetPort` port if specified)

![](NodePort%20diagram.png)

- **LoadBalancer** Services, if deployed on a cloud provider, allow external clients to access a dedicated port on a cloud provider's load balancer, which distributes traffic amongst the Pods that match the selection criteria

- If you want/need both IPv4 and IPv6 networking (e.g., for IoT), use the option `ipFamilyPolicy: PreferDualStack`

Demo:

- Apply `deploy.yml` to create a Deployment of 10 Pods
- Apply `svc.yml` to create a NodePort Service
- Apply `load-balancer.yml` to create a LoadBalancer Service

```
> kubectl get svc
NAME         TYPE           CLUSTER-IP       EXTERNAL-IP   PORT(S)          AGE
cloud-lb     LoadBalancer   10.96.90.158     localhost     9000:32199/TCP   4s
kubernetes   ClusterIP      10.96.0.1        <none>        443/TCP          3d21h
svc-test     NodePort       10.108.210.196   <none>        8080:30001/TCP   9m32s
```

- localhost:9000 resolves and displays the page; this goes to the load balancer
- localhost:30001 resolves; this is the node port that reroutes
- localhost:8080 does not resolve
- localhost:32199 does not resolve
