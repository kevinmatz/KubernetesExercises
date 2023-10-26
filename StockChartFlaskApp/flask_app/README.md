# Stock Chart web app

* To run locally:
  * `python -m pip install -r requirements.txt`
  * `python -m flash --app main run`
  *  Access the application via [http://localhost:5000/](http://localhost:5000/)

* To build and locally run the docker container:
  * `.\build_and_run_docker_container.bat` (for Windows, needs conversion to a shell script for Linux)
  * Access the application via [http://localhost:56733/](http://localhost:56733/)

* The container's name is `stockchartapp` and the fully-qualified name is `kevinmatz/stockchartapp`

* To stop the container running locally, use:
  * `docker rm -f stockchartapp` (the fully-qualified name doesn't work here, sadly)

* To push the container to Docker Hub as `kevinmatz/stockchartapp`, run:
  * `push_container_to_dockerhub.bat`

* To run the app on a Kubernetes cluster on your local Docker Desktop instance:
  * `kubectl apply -f k8s_deploy.yml`

* This sets up a Deployment with 3 replicas of Pods containing the `kevinmatz/stockchartapp` container (only), running on 3 nodes; these listen on container port 80 
* There is a Service called `stockchartappservice` that other Pods can use as their DNS configurations are set up to recognize it on the internal network (but external users cannot access this)
* A Load Balancer exists which listens on port 9000 and forwards to the Pods/containers on their port 80
* To access the Load Balancer while running the Kubernetes Cluster on your local Docker Desktop, use URL [http://localhost:9000/](http://localhost:9000/)

* To view the running Pods, use `kubectl get pods`
* To log in to one of the running Pods, choose the name of one of the Pods from the above command, and use:
  * `kubectl exec --stdin --tty stockchartapp-7d9c969dcf-5hz4s -- /bin/sh`

* To shut down the cluster:
  * `kubectl delete -f k8s_deploy.yml`
