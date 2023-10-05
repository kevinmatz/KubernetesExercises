# Notes on Kubernetes deployments

- You could write a stateless application, package it as a container, and put it in a Pod template, and this Pod could be deployed via Kubernetes as a single "static Pod"
  - "However, static Pods like this don't self-heal, they don't scale, and they don't allow for easy updates and rollbacks"
- "The Deployment controller is specifically designed for stateless apps"
- There are two components of Deployments:
  1. Deployment spec (YAML object/file)
    - This describes the desired state of the app
  2. Deployment Controller
    - Once the deployment spec YAML file is given to the API server, the Deployment Controller implements and manages it
    - The controller, on the control plane, is continuously checking the observed state and reconciles the observed state with the desired state
- Three levels of nesting in a Deployment YAML file:
  1. A **containers** holds the application
  2. A **Pod** (**Pod template**) wraps one or more containers and augments them with labels, annotations, and other metadata
  3. The **Deployment** encapsulates the **Pod**
    - Note that a Deployment object only manages a single Pod template
    - An app that has two services such as a front-end web service and a shopping cart service will have two Deployment objects
- Although a Deployment only manages a single Pod template, it will manage multiple instances (replicas) of that same Pod
  - A Deployment spec could request, for example, 10 replicas of a front-end web service Pod
- Deployments manage ReplicaSets, and ReplicaSets manage Pods
  - It's generally not recommended to manage ReplicaSets directly; let Deployments manage them
  - Deployments manage ReplicaSets, and also add rollouts and rollbacks
  - ReplicaSets manage Pods and add self-healing and scaling
- ReplicaSets continuous perform reconciliation to ensure the right number of Pod replicas are running
- Zero-downtime rolling updates of stateless apps with Deployments
  - "Rollouts" require the application to have:
    1. Microservices must be loosely coupled, communicating with each other only via well-defined APIs
    2. Backwards and forwards compatibility (service A should be able to interact with service B with a reasonable range of recent API versions of service B)
      - During a rollout of a new version, if there are 5 replicas, Kubernets will create a new replica running the new version and terminate an old replica running the previous version, and repeats until all the replicas are on the new version; during the rollout other services may connect to instances of either the old or the new version of this service in the replica set
- A Deployment manifest/specification YAML file defines:
  1. The number of Pod replicas
  2. What image(s) to use for the container(s) in the Pod
  3. What network ports to expose
  4. Details on performing rolling updates
- Deployment manifest YAML files should be kept under version control
- If you have updated a microservice with a new version, you just update the same YAML file (with the new version's container image(s)) and post it to the API server again; the Deployment then reconciles
  - Behind the scenes, Kubernetes crates a second ReplicaSet for managing the replicas with the new image
  - "As Kubernetes increases the number of Pods in the new ReplicaSet it decreases the number of Pods in the old ReplicaSet. Net result, you get a smooth incremental rollout with zero downtime."
  - The old ReplicaSet is retained with its configuration intact to enable *rollbacks*
- Apply a deployment file as usual with `kubectl apply -f deploy.yml`
- `kubectl get deploy hello-deploy`
  - shows a one-liner status of how many pods are "Ready" (e.g., "10/10"), "Up-to-date", "Available"
- `kubectl describe deploy hello-deploy`
  - shows an extended listing of status
- `kubectl get rs`
  - shows status of ReplicaSets
  - After performing an initial rollout, there will be only one ReplicaSet; its name will be the name of the Deployment with a hash suffix, such as: `hello-deploy-58d896b8d6`
- `kubectl describe rs hello-deploy-58d896b8d6`
  - described the ReplicaSet including a log of events (e.g., "SuccessfulCreate")
- **Scaling**
  1. Can do it imperatively like this:
    - `kubectl scale deploy hello-deploy --replicas 5`
      - `kubectl get deploy hello-deploy` now shows Ready: 5/5, Up-to-date: 5, Available: 5
    - ...but now the state of the environmnet doesn't match the declarative manifest file, which can cause problems with future deployments (or at least problems due to unexpected results where you don't think about the difference between the actual state and the declarative manifest)
  2. Obviously it's better to do it declaratively by changing the Deployment manifest YAML file and re-posting it to the API server
  3. Note that scaling operations are near-instantaneous, as compared to rolling updates
- **Rollouts** (a.k.a. **rolling updates**, **releases**, **zero-downtime updates**)
  - Update operations are *replacement* operations: Kubernetes will "update" a Pod by terminating it and replacing it with a new Pod with the new container image(s)
  - Update the YAML file and change the version number on the container image (e.g., from `image: nigelpoulton/k8sbook:1.0` to `image: nigelpoulton/k8sbook:2.0`), then run `kubectl apply -f <filename>`
  - You can observe using:
    - `kubectl get deploy hello-deploy --watch`
    - `kubectl get pods --watch`
    - `kubectl rollout status deployment hello-deploy`
  - You can pause and restart a rollout using:
    - `kubectl rollout pause deploy hello-deploy`
    - `kubectl rollout resume deploy hello-deploy`
- Attributes in the deployment manifest YAML file relevant for control of rollouts:

```
spec:
  replicas: 10
  selector:
    matchLabels:
      app: hello-world
  revisionHistoryLimit: 5         # Keep 5 ReplicaSets on file to roll back to
  progressDeadlineSeconds: 300    # Each Pod replica has 5 minutes to come up before the rollout is considered stalled
  minReadySeconds: 10             # Every new replica must be up and stable for 10 seconds before Kubernetes starts replacing the next one (throttling)
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1           # Minimum of 9 Pods at any time during rollout
      maxSurge: 1                 # Maximum of 11 Pods at any time during rollout
```
  - With this configuration, Kubernetes will use the delta of 11 - 9 = 2 and update Pods 2 at a time
- **Rollbacks**
  - Kubernetes maintains a history of rollouts; to view, use:
    - `kubectl rollout history deployment hello-deploy`
  - Old ReplicaSet objects are retained (up to the limit you specify in the `revisionHistoryLimit` attribute); previous ReplicaSets have 0 Pods/nodes active
    - View using:
      - `kubectl get rs`
      - `kubectl describe rs hello-deploy-58d896b8d6`
  - Rollbacks *are* rollouts, they are just rolling out the older image
  - Not recommended, but you can imperatively do a rollback like this:
    - `kubectl rollout undo deployment hello-deploy --to-revision=1`
      - After this, `kubectl describe deployment hello-deploy` shows `Image: nigelpoulton/k8sbook:1.0` for the deployment (i.e., all Pods are on this version)
    - Again, not recommended, as the actual state does not match the declarative state
  - But the book does not show an example of how to do a rollback declaratively
    - I guess if you have kept the previous version of the deployment manifest file in version control, you can retrieve it and apply it to the API server?
      - But does that re-use the previous ReplicaSet???
- Rollout behavior vis-a-vis labels:
  - In older versions of Kubernetes, a Deployment would take over management of existing static Pods if they had the same labels as the label(s) in the Deployment
  - Now, this does not happen because Kubernetes applies a system-generated `pod-template-hash` label to Pods created by a Deployment/ReplicaSet so that the Deployment only manages the Pods it has created
- **Cleanup**
  - `kubectl delete -f deploy.yml`
  - `kubectl delete -f svc.yml`
