# Notes on Kubernetes ConfigMaps and Secrets

- When using Kubernetes, you want to separate apps from their configuration; this way you can have a single app that you can deploy to Dev, Test, Prod environments without having to rebuild containers to include configuration

- ConfigMaps are key-value pair dictionaries for configuration details (attributes or whole config files) that are not sensitive, such as environment variables, account names, hostnames and ports, config files, etc.
- Kubernetes will inject data from ConfigMaps directly into containers at runtime by placing them into:
  1. environment variables
  2. arguments to the container's startup command
  3. files in a volume

- Apps can also use the Kubernetes API to access ConfigMaps to read values
  - A *Kubernetes-native application* is an application that knows it is running on Kubernetes and can interact with the Kubernetes API

- It's not recommended to create ConfigMaps imperatively but you can do so
- e.g., `kubectl create cm testmap1 --from-literal shortname=AOS --from-literal longname="Agents of Shield"`
- `kubectl describe cm testmap1` presents:

```
Name:         testmap1
Namespace:    default
Labels:       <none>
Annotations:  <none>

Data
====
longname:
----
Agents of Shield
shortname:
----
AOS

BinaryData
====

Events:  <none>
```

- Can view as a YAML file using `kubectl get cm testmap1 -o yaml`:

```
apiVersion: v1
data:
  longname: Agents of Shield
  shortname: AOS
kind: ConfigMap
metadata:
  creationTimestamp: "2023-10-14T20:52:17Z"
  name: testmap1
  namespace: default
  resourceVersion: "1155305"
  uid: 5faa6077-f8b0-4b13-b37b-2ffc44521973
```

- Create a file `cmfile.txt` containing text such as `Hello` (may contain multiple lines)
- `kubectl create cm testmap2 --from-file cmfile.txt` creates a ConfigMap named `testmap2` with a key-value pair with the key named `cmfile.txt` and the value `Hello`

- It is recommended to create ConfigMaps through declarative YAML files
- Note that ConfigMap objects don't have a concept of "state" with desired state and actual state; there is just a `data` block rather than a `spec` block in the YAML declaration
- Example `multimap.yml` file that can be applied using `kubectl apply -f multimap.yml`:

```
apiVersion: v1
kind: ConfigMap
metadata:
  name: multimap
data:
  given: Bob
  family: Smith
```

- Use this syntax to include a multi-line file:

```
apiVersion: v1
kind: ConfigMap
metadata:
  name: test-config
data:
  test-conf: |
    env = plex-test1
    endpoint = 1.2.3.4:123
    log-size = 128M
```

- **Injecting key-value pairs as environment variables in a container**
  - This can be convenient, but beware that environment variables are "static"; if you update the declaration for environment variables, existing running containers will not get those updates, only containers created in the future
  - Map the ConfigMap entries to destination environment variables in the Pod definitions like this. This example will map `given: Bob` from the `multimap` ConfigMap to an environment `FIRSTNAME: Bob` in the `container1` container, and similar for `LASTNAME: Smith`:

```
apiVersion: v1
kind: Pod
...
spec:
  containers:
    - name: container1
      ...
      env:
        - name: FIRSTNAME
          valueFrom:
            configMapKeyRef:
              name: multimap
              key: given
        - name: LASTNAME
          valueFrom:
            configMapKeyRef:
              name: multimap
              key: family
...
```

- Example (after applying `multimap.yml` earlier):

```
PS C:\GitRepos\TheK8sBook\configmaps> type envpod.yml
apiVersion: v1
kind: Pod
metadata:
  labels:
    chapter: configmaps
  name: envpod
spec:
  containers:
    - name: ctr1
      image: busybox
      command: ["sleep"]
      args: ["infinity"]
      env:
        - name: FIRSTNAME
          valueFrom:
            configMapKeyRef:
              name: multimap
              key: given
        - name: LASTNAME
          valueFrom:
            configMapKeyRef:
              name: multimap
              key: family
PS C:\GitRepos\TheK8sBook\configmaps> kubectl apply -f envpod.yml
pod/envpod created
PS C:\GitRepos\TheK8sBook\configmaps> kubectl exec envpod -- env
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
HOSTNAME=envpod
FIRSTNAME=Bob
LASTNAME=Smith
KUBERNETES_SERVICE_HOST=10.96.0.1
KUBERNETES_SERVICE_PORT=443
KUBERNETES_SERVICE_PORT_HTTPS=443
KUBERNETES_PORT=tcp://10.96.0.1:443
KUBERNETES_PORT_443_TCP=tcp://10.96.0.1:443
KUBERNETES_PORT_443_TCP_PROTO=tcp
KUBERNETES_PORT_443_TCP_PORT=443
KUBERNETES_PORT_443_TCP_ADDR=10.96.0.1
HOME=/root
```

- **Injecting key-value pairs into container startup commands**
  - When specifying a container in a Pod definition, you can supply an initial command to be run in the container, and you can insert values from a ConfigMap into this command. This is done by defining environment variables as before, and then using `${VARIABLENAME}` to insert the value of an environment variable.
  - This method works well but again won't update existing running containers. Only newly-created containers will have the startup command run with the new values.
  - Example:

```
PS C:\GitRepos\TheK8sBook\configmaps> type startuppod.yml
apiVersion: v1
kind: Pod
metadata:
  name: startup-pod
  labels:
    chapter: configmaps
spec:
  restartPolicy: OnFailure
  containers:
    - name: args1
      image: busybox
      command: [ "/bin/sh", "-c", "echo First name $(FIRSTNAME), last name $(LASTNAME)", "wait" ]
      env:
        - name: FIRSTNAME
          valueFrom:
            configMapKeyRef:
              name: multimap
              key: given
        - name: LASTNAME
          valueFrom:
            configMapKeyRef:
              name: multimap
              key: family
PS C:\GitRepos\TheK8sBook\configmaps> kubectl apply -f startuppod.yml
pod/startup-pod created
PS C:\GitRepos\TheK8sBook\configmaps> kubectl logs startup-pod -c args1
First name Bob, last name Smith
PS C:\GitRepos\TheK8sBook\configmaps> kubectl describe pod startup-pod
Name:             startup-pod
...
Containers:
  args1:
    Container ID:  docker://23ce08b6f9a622644f899e767e16368f9638272178a7cf425ef38c06a665f7ae
...
    Environment:
      FIRSTNAME:  <set to the key 'given' of config map 'multimap'>   Optional: false
      LASTNAME:   <set to the key 'family' of config map 'multimap'>  Optional: false
...
```

- **Using ConfigMaps and volumes**
  - Entire configuration files can be updated this way in running containers
  - Steps:
    1. Create ConfigMap
    2. Create a **ConfigMap volume** in the Pod template
    3. Mount the ConfigMap volume in the container
    4. Entries from the ConfigMap will appear in the volume/container as individual files
  - But beware that changes are **not instantaneous; it can take up to about a minute for the changes to be applied**
  - Example:

```
PS C:\GitRepos\TheK8sBook\configmaps> type cmpod.yml
apiVersion: v1
kind: Pod
metadata:
  name: cmvol
spec:
  volumes:
    - name: volmap
      configMap:
        name: multimap
  containers:
    - name: ctr
      image: nginx
      volumeMounts:
        - name: volmap
          mountPath: /etc/name
PS C:\GitRepos\TheK8sBook\configmaps> kubectl apply -f cmpod.yml
pod/cmvol created
PS C:\GitRepos\TheK8sBook\configmaps> kubectl exec cmvol -- ls /etc/name
family
given
PS C:\GitRepos\TheK8sBook\configmaps> kubectl exec cmvol -- cat /etc/name/family
Smith
PS C:\GitRepos\TheK8sBook\configmaps> kubectl exec cmvol -- cat /etc/name/given
Bob
```

- If you then post a new ConfigMap YAML file, it will update the files in the volume, but after a delay (in this case about 30 seconds):

```
PS C:\GitRepos\TheK8sBook\configmaps> copy multimap.yml multimap2.yml
PS C:\GitRepos\TheK8sBook\configmaps> notepad multimap2.yml
PS C:\GitRepos\TheK8sBook\configmaps> kubectl apply -f multimap2.yml
configmap/multimap configured
PS C:\GitRepos\TheK8sBook\configmaps> kubectl exec cmvol -- cat /etc/name/family
Smith
PS C:\GitRepos\TheK8sBook\configmaps> kubectl exec cmvol -- cat /etc/name/family
Smith
PS C:\GitRepos\TheK8sBook\configmaps> kubectl exec cmvol -- cat /etc/name/family
Smith
PS C:\GitRepos\TheK8sBook\configmaps> kubectl exec cmvol -- cat /etc/name/family
Doe
PS C:\GitRepos\TheK8sBook\configmaps> kubectl exec cmvol -- cat /etc/name/given
John
```

- Note that you can add new key/value pairs or remove ones and the volume will be updated to match:

```
PS C:\GitRepos\TheK8sBook\configmaps> notepad multimap2.yml
PS C:\GitRepos\TheK8sBook\configmaps> kubectl apply -f multimap2.yml
configmap/multimap configured
PS C:\GitRepos\TheK8sBook\configmaps> kubectl exec cmvol -- ls /etc/name
family
given
PS C:\GitRepos\TheK8sBook\configmaps> kubectl exec cmvol -- ls /etc/name
city
family
```

- **Secrets**
  - Secrets are similar to ConfigMaps but are for sensitive data like API keys, passwords, certificates, OAuth tokens, etc.
  - Kubernetes does not actually encrypt secrets at rest in the cluster store (it does encode them as base-64 but that can be effortlessly decoded)
  - Secrets are also transmitted unencrypted over the network (although, generally, service meshes encrypt network traffic)
  - You can use `EncryptionConfiguration` objects and/or third-party secrets management tools like HashiCorp Vault
    - But then the Secret is mounted as plain-text in the target container so that the application can consume it; this is done using a `tmpfs` filesystem which is in-memory so the plain-text secret is not persisted to a disk/volume in a node
  - Secrets are limited to 1MB in size

- To create secrets imperatively:

```
PS C:\GitRepos\TheK8sBook\configmaps> kubectl create secret generic creds --from-literal user=nigelpoulton --from-literal pwd=Password123
secret/creds created
PS C:\GitRepos\TheK8sBook\configmaps> kubectl get secret creds -o yaml
apiVersion: v1
data:
  pwd: UGFzc3dvcmQxMjM=
  user: bmlnZWxwb3VsdG9u
kind: Secret
metadata:
  creationTimestamp: "2023-10-14T22:30:49Z"
  name: creds
  namespace: default
  resourceVersion: "1163864"
  uid: 435d77bf-f52c-44ec-8584-7594d747f288
type: Opaque
PS C:\GitRepos\TheK8sBook\configmaps> echo UGFzc3dvcmQxMjM= | base64 -d
Password123
```

- To create secrets declaratively, use `data:` if specifying Base64 values or `stringData:` if specifying plain-text values:

```
apiVersion: v1
kind: Secret
metadata:
  name: tkb-secret
  labels: 
    chapter: configmaps
type: Opaque
data:
  username: bmlnZWxwb3VsdG9u
  password: UGFzc3dvcmQxMjM=
```

- To inject a Secret into a container, use **Secret volumes**. Example:

```
PS C:\GitRepos\TheK8sBook\configmaps> type secretpod.yml
apiVersion: v1
kind: Pod
metadata:
  name: secret-pod
  labels:
    topic: secrets
spec:
  volumes:
  - name: secret-vol
    secret:
      secretName: tkb-secret
  containers:
  - name: secret-ctr
    image: nginx
    volumeMounts:
    - name: secret-vol
      mountPath: "/etc/tkb"
      readOnly: true
PS C:\GitRepos\TheK8sBook\configmaps> kubectl apply -f secretpod.yml
pod/secret-pod created
PS C:\GitRepos\TheK8sBook\configmaps> kubectl exec secret-pod -- ls /etc/tkb
password
username
PS C:\GitRepos\TheK8sBook\configmaps> kubectl exec secret-pod -- cat /etc/tkb/password
Password123
```

- Finally, `kubectl delete secrets tkb-secret, creds` to clean up (should also delete ConfigMaps and Pods)
