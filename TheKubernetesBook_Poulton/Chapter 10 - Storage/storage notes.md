# Notes on Kubernetes storage

- Kubernetes has a *persistent volume subsystem* for data/file storage and there is a third-party ecosystem with extensions for backup/recovery, remote replication, etc.
- Kubernetes can support cloud storage back-ends (e.g., AWS Elastic Block Store (EBS), Google Kubernetes Engine Persistent Disks (PD), etc.) as well as enterprise-class storage systems, on-premise or cloud, from vendors such as EMC and NetApp
  - A *plugin* based on the *Container Storage Interface (CSI)* is needed for each different type of storage resource
    - A plugin runs as its own set of Pods under the `kube-system` Namespace
    - A plugin in some contexts is called a *provisioner*
- Block/file/object storage is all exposed to Kubernetes as a *volume*

- Persistent Volume Subsystem consists of these API objects:
  - *Persistent Volumes (PV)* which map to external storage assets
  - *Persistent Volume Claims (PVC)* are like tickets that authorize applications/Pods to use PVs
  - *Storage Classes (SC)* let you define specifications for different tiers or classes of storage, e.g., fast (SSD), slow (mechanical hard drives), archive, fsat-local, fast-replicated, etc.
    - You can then dynamically create instances (physical storage resources) using these SC definitions

- Example of how things are connected:
  1. Admin manually creates an AWS EBS volume called `ebs-vol`
  2. Admin creates a PV called `k8s-vol` that maps to `ebs-vol` via a CSI plugin `ebs.csi.aws.com`
  3. The PV now represents the access point to the volume on the Kubernetes cluster
  4. A Pod can use a PVC to claim access to the PV to start using the volume
- Notes on this example:
  - Normally SCs would be used to automate some of these steps, rather than manual admin actions
  - Rules generally prevent multiple Pods from accessing the same volume
  - You cannot map an external volume to multiple PVs (e.g., spreading a 50GB volume across two 25GB PVs)

- StorageClass YAML
  - details are very specific/dependent upon the vendor and plugin; always need to check the plugin's documentation
  - specify the plugin via the `provisioner` attribute; sample values: `pd.sci.storage.gke.io`, `io.hedvig.csi`
  - `accessModes` supports three options:
    1. `ReadWriteOnce`, a PV that can be bound as read-write by a single PVC only; block storage is usually this type
    2. `ReadWriteMany`, a PV that can be bound as read-write by many PVCs; this is generally only supported for file and object storage such as NFS
    3. `ReadOnly`, PV that can be bound as read-only by many PVCs
  - Reclaim policy, indicating what Kubernetes should do with a PV when its PVC is released:
    1. `Delete`, completely deletes the PV and associated storage resource on the external storage system; all data will be lost
    2. `Retain`, keeps the PV on the cluster and keeps the data on the external storage system, but other PVCs are prevented from using it in the future
  - VolumeBindingMode:
    - `Immediate` will create the volume on the external storage system as soon as the PVC is created, which may not be desirable if you use multiple data centers/regions: the Pod that consumes it may be in a different data center/region
    - `WaitForFirstConsumer` delays creating the resource until a Pod using the PVC is created, which ensures the volume will be created in the same data center/region as the Pod

- The book's example will only work on a "regional" Google Kubernetes Engine cluster

- List all storage classes available / already defined on your environment/cluster: 
  - `kubectl get sc`
  - some SCs will generally be pre-created for you on hosted Kubernetes platforms
- See details of a storage class:
  - `kubectl describe sc <name>`
  - `kubectl get sc <name> -o yaml` to show the configuration in YAML format
- List existing PVs:
  - `kubectl get pv`
- List existing PVCs:
  - `kubectl get pvc`

- Example of a PVC definition referring to the existing StorageClass `premium-rwo` available on GKE:

```
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-prem
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: premium-rwo
  resources:
    requests:
      storage: 10Gi
```

- Example of a Pod definition that mounts this PVC by setting `claimName: pvc-prem`:

```
apiVersion: v1
kind: Pod
metadata:
  name: volpod
spec:
  volumes:
  - name: data
    persistentVolumeClaim:
      claimName: pvc-prem
  containers:
  - name: ubuntu-ctr
    image: ubuntu:latest
    command:
    - /bin/bash
    - "-c"
    - "sleep 60m"
    volumeMounts:
    - mountPath: /data
      name: data
```

- Apply both to the API server; because the SC has the volume binding mode set to `WaitForFirstConsumer`, it won't provision the volume and PV until the Pod is running and claims it
- Now `kubectl get pvc` will list a `pvc-prem` PVC referring to a volume such as `pvc-796afda3...`
- `kubectl get pv` will list a PV `pvc-796afda3...` with the "Claim" listed as `default/pvc-prem` (`default` must be the namespace)
- `kubectl get pods volpod` will mention that the PVC is mounted
- `kubectl delete pod volpod`
- `kubectl delete pvc pvc-prem`
  - Can verify that the volume on GKE will be deleted, as the `ReclaimPolicy` for this SC was set to `Delete`






