# Stock Chart web app

* To run locally:
  * `python -m pip install -r requirements.txt`
  * `python -m flash --app main run`
  *  Access the application via [http://localhost:5000/](http://localhost:5000/)

* To package the app into a Docker container using the Dockerfile, and then locally run the Docker container:
  * `.\build_and_run_docker_container.bat` (for Windows obviously; this can be easily converted to a shell script for Linux)
  * Access the application via [http://localhost:56733/](http://localhost:56733/)

* The container's name is `stockchartapp` and the fully-qualified name is `kevinmatz/stockchartapp`

* To stop the container running locally, use:
  * `docker rm -f stockchartapp` (the fully-qualified name doesn't work here, sadly)

* To push the container to Docker Hub as `kevinmatz/stockchartapp`, run:
  * `push_container_to_dockerhub.bat`
  * Verify on Docker Hub at: [https://hub.docker.com/repository/docker/kevinmatz/stockchartapp/general](https://hub.docker.com/repository/docker/kevinmatz/stockchartapp/general)
  * Note that this is currently a public repository; if the project is changed to use databases or other resources that require Secrets, then it should be set to private

* To run the app on a Kubernetes cluster on your local Docker Desktop instance:
  * `kubectl apply -f k8s_deploy.yml`

* This creates a namespace `financefun` and all of the following objects are added to that namespace, so most `kubectl` commands will need to add a `-n financefun` argument to specify the namespace
* This sets up a Deployment with 3 replicas of Pods containing the `kevinmatz/stockchartapp` container (only), running on 3 nodes; these listen on container port 80 
* There is a Service called `stockchartappservice` that other Pods can use as their DNS configurations are set up to recognize it on the internal network (but external users cannot access this)
* A Load Balancer exists which listens on port 9000 and forwards to the Pods/containers (on their port 80) in the Deployment/ReplicaSet
* To access the Load Balancer while running the Kubernetes Cluster on your local Docker Desktop, use URL [http://localhost:9000/](http://localhost:9000/)

* To view the running Pods, use `kubectl get pods -n financefun`
* To log in to one of the running Pods, choose the name of one of the Pods from the above command, and use:
  * `kubectl exec --stdin --tty stockchartapp-7d9c969dcf-5hz4s -n financefun -- /bin/sh`

* To shut down the cluster:
  * `kubectl delete -f k8s_deploy.yml`

* A ConfigMap `stockmarketconfig` has been created (within the `financefun` namespace) with the single key-value pair `data-provider: Yahoo! Finance`
  * The container is then configured to have the value set as the environment variable `DATAPROVIDER`, and the application reads that environment variable and displays the value in the footer of the pages of the app

* Notes on deploying to AWS EKS (Elastic Kubernetes Service):
  * [https://us-east-1.console.aws.amazon.com/eks/home?region=us-east-1#/cluster-create](https://us-east-1.console.aws.amazon.com/eks/home?region=us-east-1#/cluster-create)
  * "Configure Cluster"
  * Name: `KevinsTestCluster1`
  * Kubernetes version: 1.28
  * Creating a cluster service role as per the instructions in [https://docs.aws.amazon.com/eks/latest/userguide/service_IAM_role.html#create-service-role](https://docs.aws.amazon.com/eks/latest/userguide/service_IAM_role.html#create-service-role)
    * Role name: `MyAWSServiceRoleForEKS` (won't let me use the `AWSServiceRole` prefix like I did for past roles)
  * Not enabling Secrets Protection because not using Secrets yet
  * Selected default VPC (Virtual Private Cloud) offered (created ages ago)
  * Accepted offered subnets (6 total)
  * Selected the existing default security group for VPC
  * Kept the default of IPv4
  * Not configuring a service IP range
  * Cluster endpoint access: "Public and private", "The cluster endpoint is accessible from outside of your VPC. Worker node traffic to the endpoint will stay within your VPC."
  * Control plane logging: Enabled "API Server" but left the other options unchecked
  * Select add-ons: kept the defaults, didn't add anything new
  * Configure add-ons settings: kept all the defaults, no changes
  * "Cannot create cluster 'KevinsTestCluster1' because us-east-1e, the targeted availability zone, does not currently have sufficient capacity to support the cluster. Retry and choose from these availability zones: us-east-1a, us-east-1b, us-east-1c, us-east-1d, us-east-1f"
    * Removed "use-east-1e" from the list of subnets, tried again, it proceeded
  * Reviewing [https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html](https://docs.aws.amazon.com/eks/latest/userguide/getting-started.html) and [https://docs.aws.amazon.com/eks/latest/userguide/getting-started-eksctl.html](https://docs.aws.amazon.com/eks/latest/userguide/getting-started-eksctl.html)
  * Updating `aws-cli` on Windows via: `msiexec.exe /i https://awscli.amazonaws.com/AWSCLIV2.msi`
  * Installing `eksctl` using installer from [https://eksctl.io/installation/](https://eksctl.io/installation/); put eksctl.exe file in `C:\DevTools\eksctl` and added to PATH
  * Running: `eksctl create cluster --name KevinsTestCluster2 --region us-east-1 --fargate`
    * Doing it this way (versus the manual creation done above) has the advantage of adding entries to the `.kube/config` file
    * Indeed, the `kubeconfig` file has been updated with a cluster entry, a user entry, a new context entry matching these up, and the `current-context` has been set to this new context:
```
contexts:
  ...
  - context:
    cluster: KevinsTestCluster2.us-east-1.eksctl.io
    user: kevinmatz@KevinsTestCluster2.us-east-1.eksctl.io
  name: kevinmatz@KevinsTestCluster2.us-east-1.eksctl.io
current-context: kevinmatz@KevinsTestCluster2.us-east-1.eksctl.io
```

* (resuming bullet point list)
  * If you need to change `kubeconfig` to match a manually-created cluster, see: [https://docs.aws.amazon.com/eks/latest/userguide/create-kubeconfig.html](https://docs.aws.amazon.com/eks/latest/userguide/create-kubeconfig.html)
  * Checking that we're connected to EKS:

```
PS C:\WINDOWS\system32> kubectl get services
NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
kubernetes   ClusterIP   10.100.0.1   <none>        443/TCP   17m
PS C:\WINDOWS\system32> kubectl get pods
No resources found in default namespace.
```

* Navigating in AWS console to KevinsTestCluster2, the API server endpoint for Kubernetes is: `https://afae948df68696dd017eec21e2d3e611.gr7.us-east-1.eks.amazonaws.com/` -- but note that this is the API Server, not the application's external endpoint

```
PS C:\GitRepos\KubernetesExercises\StockChartFlaskApp\flask_app> kubectl get all -n financefun
NAME                                READY   STATUS    RESTARTS   AGE
pod/stockchartapp-f444fdbbb-cjsmf   0/1     Pending   0          7m13s
pod/stockchartapp-f444fdbbb-mqpbd   0/1     Pending   0          7m13s
pod/stockchartapp-f444fdbbb-qrt4q   0/1     Pending   0          7m13s

NAME                           TYPE           CLUSTER-IP       EXTERNAL-IP                                                              PORT(S)          AGE
service/cloud-loadbalancer     LoadBalancer   10.100.236.204   a26a7e63751df443087c1feb7d448b64-289481390.us-east-1.elb.amazonaws.com   9000:32474/TCP   7m13s
service/stockchartappservice   NodePort       10.100.45.197    <none>                                                                   8080:30001/TCP   7m13s

NAME                            READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/stockchartapp   0/3     3            0           7m14s

NAME                                      DESIRED   CURRENT   READY   AGE
replicaset.apps/stockchartapp-f444fdbbb   3         3         0       7m14s
```

* Viewing all the resources created under CloudFormation in AWS console
  * Cluster: `eksctl-KevinsTestCluster2-cluster`
* Navigating in AWS console to "Elastic Load Balancers", a load balancer has been created and the DNS name is shown as:
  * `a26a7e63751df443087c1feb7d448b64-289481390.us-east-1.elb.amazonaws.com`
  * However, this doesn't work in my browser, and trying ports like :9000 and :80 don't work either
  * Tried adding an "All Traffic" security rule and various variations under Security Groups --> Inbound Rules, but no luck

* Wrapping up this session for now...
  * Shutting down via `kubectl delete -f .\k8s_deploy.yml`
  * `eksctl delete cluster --name KevinsTestCluster2 --region us-east-1`

* Next steps: Currently the Service with "type: LoadBalancer" is set up with "port: 9000" (the port the Service is listening on) and "targetPort: 80" but ChatGPT suggested 9000 should be changed to 80 for normal HTTP traffic
