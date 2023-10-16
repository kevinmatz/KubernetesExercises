# Notes on Kubernetes StatefulSets

- StatefulSets (`sts`) facilitate operating stateful applications -- applications that persist data, such as in a database or other data store -- on Kubernetes
- StatefulSets are like Deployments (so they define a Pod template with container(s), and define how many replica instances of that Pod template should exist, and a Controller manages the deployment) but they guarantee predictable and persistent...
  1. Pod names
  2. DNS hostnames
  3. volume bindings
- ...this set of properties is called the "state" of a Pod, or its "**sticky ID**", and StatefulSets ensure that this state/sticky ID is persisted across scaling and failures
- This enables having unique, reliable Pods for certain purposes
- If Pods managed by a StatefulSet fail, they will be replaced with Pods with the same Pod name, DNS hostname, and volumes, even if the replacement is started on a different cluster node

- If a StatefulSet is declared with a name `tkb-sts`, then the first Pod created is given the number 0 and is named `tkb-sts-0`; the next will be 'tkb-sts-1`, etc.
- To avoid race conditions, a StatefulSet will create one Pod at a time, and wait for the previous Pod to be "running and ready" (ready to service requests) before creating the next one (contrast with Deployments with a ReplicaSet controller, which will start all the Pods at the same time)
  - This is also done for scaling operations

- When deleting StatefulSets, note:
  1. Deleting a StatefulSet will not shut down the replicas in order, so you may want to scale it down to 0 replicas first
  2. Use the `terminationGracePeriodSeconds` attribute to give at least 10 seconds to applications to flush buffers and commit writes in progress

- When a StatefulSet's Pods are created for the first time, new volumes are provisioned and connected to the Pods (e.g., `tkb-sts-0` connected to `vol-tkb-sts-0`) using Persistent Volume Claims
  - These volumes have separate lifecycles than their associated Pods
  - If a Pod fails or is terminated, the associated volume survives
  - A replacement Pod then attaches to the same volume (even if the new Pod is established on a separate cluster node)
  - For scaling operations, if a Pod is deleted as part of a scale-down, its volume will survive and later scale-ups will attach the new Pods to volumes that match their names

- Pod failures
  - If a Pod fails, and Kubernetes is absolutely certain that the Pod failed or was terminated, the controller will restart a new Pod to replace it
  - If a Pod were to fail but Kubernetes could not be absolutely certain (it's not sure if there is a network partition or the Pod is rebooting, etc.), there would be the chance that, if the failed Pod eventually recovered after Kubernetes were to replace it with a new one, it would connect to the same volume and two Pods writing to the same volume would result in data corruption
    - So Kubernetes is careful; "manual intervention is needed before Kubernetes will replace Pods that it *thinks* have failed" (but cannot 100% be certain)

- Headless services
  - If other parts of the application need to be able to connect to individual Pods, you can configure a **headless service** in the StatefulSet definition
  - A headless service is a Service without an IP address (`spec.clusterIP` = None); you declare it under `spec.serviceName` in the StatefulSet YAML and this becomes the "governing Service"
  - The headless Service is established with DNS SRV records so that it (actually, the individual Pods???) has a predictable DNS hostname available for lookup; clients can use DNS to look up reach Pods directly (so the headless Service doesn't need a ClusterIP)

- The example in the book is set up to run on Google Kubernetes Engine (GKE) only

- Define a StorageClass (on GKE) and deploy it:

```
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: flash
provisioner: pd.csi.storage.gke.io
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
parameters:
  type: pd-ssd
```

- Define and apply a headless Service (it's headless because `clusterIP: None`):

```
# Headless Service for StatefulSet Pod DNS names
apiVersion: v1
kind: Service
metadata:
  name: dullahan
  labels:
    app: web
spec:
  ports:
  - port: 80
    name: web
  clusterIP: None
  selector:
    app: web
```

- Define and deploy a StatefulSet `tkb-sts` with 3 replicas `tkb-sts-0`, `tkb-sts-1`, `tks-sts-2` and a governing Service (headless Service) named `dullahan`:
  - With StatefulSets with replicas, so that each Pod gets its own separate volume, use `volumeClaimTemplates` which creates a PVC each time the StatefulSet controller creates a new Pod replica; it will name it and connect it to the correct Pod

```
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: tkb-sts
spec:
  replicas: 3 
  selector:
    matchLabels:
      app: web
  serviceName: "dullahan"
  template:
    metadata:
      labels:
        app: web
    spec:
      terminationGracePeriodSeconds: 10
      containers:
      - name: ctr-web
        image: nginx:latest
        ports:
        - containerPort: 80
          name: web
        volumeMounts:
        - name: webroot
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
  - metadata:
      name: webroot
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "flash"
      resources:
        requests:
          storage: 1Gi
```

- `kubectl get sts --watch` shows the StatefulSet and its replicas; it will show under "READY" first "0/3", then "1/3", "2/3", "3/3" as the replicas start up one after another (about 30 seconds for each)
- `kubectl get pvc` shows the PVCs named `webroot-tkb-sts-0` .. `2`, with each one's volume listed

- Now, to look up Pods using the DNS SRV records, the pattern for DNS subdomains is:
  - `<object-name>.<service-name>.<namespace>.svc.cluster.local`
  - So in this example, the three Pods will have these fully-qualified DNS names:
    - `tkb-sts-0.dullahan.default.svc.cluster.local`
    - `tkb-sts-1.dullahan.default.svc.cluster.local`
    - `tkb-sts-2.dullahan.default.svc.cluster.local`

- Deploy a "jump pod" that has `curl` installed:

```
apiVersion: v1
kind: Pod
metadata:
  name: jump-pod
spec:
  terminationGracePeriodSeconds: 1
  containers:
  - image: nigelpoulton/curl:1.0
    name: jump-ctr
    tty: true
    stdin: true
```

- `kubectl exec -it jump-pod -- bash`
- The linux `dig` command is a tool for interrogating DNS name servers
- `dig SRV dullahan.default.svc.cluster.local`
  - this shows the fully-qualified domain names `tkb-sts-0.dullahan.default.svc.cluster.local`, etc., for each Pod, and the IP addresses for each
- Applications can use this method to discover the currently-running Pods in the StatefulSet, and connect to them; applications need to know the name of the headless service, i.e., `dullahan.default.svc.cluster.local`

- When the StatefulSet is scaled down, the Pods are terminated but the PVCs are not
- Edit the abov StatefulSet YAML definition and change the replica count from 3 to 2 and redeploy it
- `kubectl get sts tkb-sts` and `kubectl get pods` show 2 Pods
- `kuebctl get pvc` shows that PVC `webroot-tkb-sts-2` is still available (and status shows as "Bound")
- Change replicas back to 3 and redeploy and run the above commands again; there are 3 Pods and the new Pod `tkb-sts-2` has mounted the existing `webroot-tkb-sts-2` volume
- If you delete a Pod (simulating a failure), using `kubectl get pods --watch` you can see the Pod being terminated, and then a new one with the same name is started (goes through states `Pending`, `ContainerCreating`, `Running`)
  - Kubernetes created a new Pod in this case because it was 100% certain about the Pod's "failure" through the intentional termination; otherwise, manual recovery/intervention would be needed

- More control over starting/stopping of Pods can be achieved using `spec.podManagementPolicy`
  - `Parallel` starts/stops Pods simultaneously instead of waiting for each to be ready or to terminate

- **Rollouts**
  - If you change the container image(s), the StatefulSet controller will replace all the old Pods with new ones, but one at a time, and it starts with the highest-numbered Pod and works down

- **Deleting StatefulSets**
  - If your app is sensitive to ordered shutdown of these Pods, scale the replicas to 0
    - Edit and post the YAML file, or, do it imperatively like this:
      - `kubectl scale sts tkb-sts --replicas=0`
  - Then you can delete: `kubectl delete sts tkb-sts` or `kubectl delete -f <YAML file>`
  - This will remove all the DNS SRV records
  - The headless Service, the volumes, the StorageClass, and the "jump Pod" will still exist; generally you would want to preserve the volumes for a production app, but beware that volumes would continue to incur costs on the cloud platform
