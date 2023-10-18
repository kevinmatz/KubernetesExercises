# Notes on the Kubernetes API

- You can use `kubectl` to issue requests
- Programs can also use the Kubernetes API to issue requests

- When using `kubectl`, it serializes requests into JSON format
- Programs that use the Kubernetes REST API can send requests using JSON objects in HTTP requests with `Content-Type: application/json` and Kubernetes will respond with JSON objects
- Kubernetes can also serialize requests in a more compact and efficient form using Protobuf; this is generally only used for internal cluster traffic whereas JSON, which is more human-readable, is used with external clients

- API request flow:
  1. Client (`kubectl` or code) submits a request
  2. API server does authorization, authentication, admission control
  3. API processes request
  4. Scheduler
  5. Cluster store

- The API server runs as a set of Pods in the `kube-system` Namespace, on the control plane nodes of your cluster
  - A hosted Kubernetes cluster will ensure the control plane nodes are redundant and high-availability

- `kubectl proxy --port 9000 &` will start a proxy that exposes the REST API on your `localhost` adapter; authentication is taken care of
  - "`Starting to serve on 127.0.0.1:9000`"
- Then you can use a tool like `curl` or Postman to issue requests against the server (use `curl -v` to show HTTP headers)
- Example (GET) while the Chapter 5 (Namespaces) example is running -- the results are under the "items" section:

```
PS C:\GitRepos\TheK8sBook\namespaces> curl -v http://localhost:9000/api/v1/namespaces/shield/pods
VERBOSE: GET http://localhost:9000/api/v1/namespaces/shield/pods with 0-byte payload
VERBOSE: received -1-byte response of content type application/json

StatusCode        : 200
StatusDescription : OK
Content           : {
                      "kind": "PodList",
                      "apiVersion": "v1",
                      "metadata": {
                        "resourceVersion": "1250993"
                      },
                      "items": [
                        {
                          "metadata": {
                            "name": "triskelion",
                            "namespace": "shield",
                     ...
RawContent        : HTTP/1.1 200 OK
                    Audit-Id: 4be41150-f6e6-4a54-be86-a40e0f9c7e8c
                    X-Kubernetes-Pf-Flowschema-Uid: b09dcdf4-6133-40bc-992f-2ba50d2dfc95
                    X-Kubernetes-Pf-Prioritylevel-Uid: 33d04e00-bcfd-46b8-8ff7-add16b...
Forms             : {}
Headers           : {[Audit-Id, 4be41150-f6e6-4a54-be86-a40e0f9c7e8c], [X-Kubernetes-Pf-Flowschema-Uid,
                    b09dcdf4-6133-40bc-992f-2ba50d2dfc95], [X-Kubernetes-Pf-Prioritylevel-Uid,
                    33d04e00-bcfd-46b8-8ff7-add16b02196b], [Transfer-Encoding, chunked]...}
Images            : {}
InputFields       : {}
Links             : {}
ParsedHtml        : mshtml.HTMLDocumentClass
RawContentLength  : 8369
```

- Example of a POST request
  - Note, this doesn't work in PowerShell on Windows because `curl` actually maps to a different command that takes different command line arguments, and the `@` operator doesn't work?  So be sure to run this in `cmd` on Windows instead:

```
C:\GitRepos\TheK8sBook\api>more ns.json
{
    "kind": "Namespace",
    "apiVersion": "v1",
    "metadata": {
      "name": "shield",
      "labels": {
        "chapter": "api"
      }
    }
}

C:\GitRepos\TheK8sBook\api> curl -X POST -H "Content-Type: application/json" --data-binary @ns.json http://localhost:9000/api/v1/namespaces
{
  "kind": "Namespace",
  "apiVersion": "v1",
  "metadata": {
    "name": "shield",
    "uid": "a51f7b28-75f5-4503-b53b-a2021b9f6310",
    "resourceVersion": "1251676",
    "creationTimestamp": "2023-10-18T19:43:17Z",
    "labels": {
      "chapter": "api",
      "kubernetes.io/metadata.name": "shield"
    },
    "managedFields": [
      {
        "manager": "curl",
        "operation": "Update",
        "apiVersion": "v1",
        "time": "2023-10-18T19:43:17Z",
        "fieldsType": "FieldsV1",
        "fieldsV1": {
          "f:metadata": {
            "f:labels": {
              ".": {},
              "f:chapter": {},
              "f:kubernetes.io/metadata.name": {}
            }
          }
        }
      }
    ]
  },
  "spec": {
    "finalizers": [
      "kubernetes"
    ]
  },
  "status": {
    "phase": "Active"
  }
}

C:\GitRepos\TheK8sBook\api>kubectl get namespaces
NAME              STATUS   AGE
default           Active   19d
ingress-nginx     Active   10d
kube-node-lease   Active   19d
kube-public       Active   19d
kube-system       Active   19d
shield            Active   3m46s

C:\GitRepos\TheK8sBook\api> curl -v -X DELETE -H "Content-Type: application/json" http://localhost:9000/api/v1/namespaces/shield
*   Trying 127.0.0.1:9000...
* Connected to localhost (127.0.0.1) port 9000 (#0)
> DELETE /api/v1/namespaces/shield HTTP/1.1
> Host: localhost:9000
> User-Agent: curl/8.0.1
> Accept: */*
> Content-Type: application/json
>
< HTTP/1.1 200 OK
< Audit-Id: 07e91597-0a5a-4fce-a95e-9ef33a493c90
< Cache-Control: no-cache, private
< Content-Length: 893
< Content-Type: application/json
< Date: Wed, 18 Oct 2023 19:47:51 GMT
< X-Kubernetes-Pf-Flowschema-Uid: b09dcdf4-6133-40bc-992f-2ba50d2dfc95
< X-Kubernetes-Pf-Prioritylevel-Uid: 33d04e00-bcfd-46b8-8ff7-add16b02196b
<
{
  "kind": "Namespace",
  "apiVersion": "v1",
  "metadata": {
    "name": "shield",
    "uid": "a51f7b28-75f5-4503-b53b-a2021b9f6310",
    "resourceVersion": "1252077",
    "creationTimestamp": "2023-10-18T19:43:17Z",
    "deletionTimestamp": "2023-10-18T19:47:51Z",
    "labels": {
      "chapter": "api",
      "kubernetes.io/metadata.name": "shield"
    },
    "managedFields": [
      {
        "manager": "curl",
        "operation": "Update",
        "apiVersion": "v1",
        "time": "2023-10-18T19:43:17Z",
        "fieldsType": "FieldsV1",
        "fieldsV1": {
          "f:metadata": {
            "f:labels": {
              ".": {},
              "f:chapter": {},
              "f:kubernetes.io/metadata.name": {}
            }
          }
        }
      }
    ]
  },
  "spec": {
    "finalizers": [
      "kubernetes"
    ]
  },
  "status": {
    "phase": "Terminating"
  }
}* Connection #0 to host localhost left intact

C:\GitRepos\TheK8sBook\api>kubectl get namespaces
NAME              STATUS   AGE
default           Active   19d
ingress-nginx     Active   10d
kube-node-lease   Active   19d
kube-public       Active   19d
kube-system       Active   19d
```

- REST paths:
  - For objects without namespaces, the typical pattern is: `/api/v1/nodes/`
  - For namespaced objects, the typical pattern in: `/api/v1/namespaces/{namespace}/pods/{pod}`
  - "Group, version, resource" pattern for objects in "named" API groups (i.e., not in the `core` API group), example: `/apis/storage.k8s.io/v1/storageClasses`

- Advanced: You can extend the API by defining your own resources via `CustomResourceDefinition` and a custom controller (outside of the scope of the book); these resources can then be manipulated CRUD-style using the Kubernetes API




