# Kubernetes Admission Webhook
Implement Kubernetes mutating webhook &amp; validating webhook

# 📌 Validating Webhook
## Create certificate
```Bash
openssl req -x509 -sha256 -newkey rsa:2048 -keyout webhook.key -out webhook.crt -days 1024 -nodes -addext "subjectAltName = DNS.1:validate.default.svc"
```

## Apply Secret
```Bash
cat webhook.key | base64 | tr -d '\n'
#LS0tLS1CRUdJTiBQUklWQVRFI....
cat webhook.crt | base64 | tr -d '\n'
#LS0tLS1CRUdJTiBDRVJUSUZJQ0FUR....
```
```YAML
apiVersion: v1
kind: Secret
metadata:
  name: admission-tls
type: Opaque
data:
  webhook.crt: YOUR ENCODED BASE64 CERT
  webhook.key: YOUR ENCODED BASE64 KEY
```

## Apply Deployment, Service, ValidatingWebhookConfiguration
make sure to modify the YAML, then check the Pod state
```
kubectl get pod
NAME                                 READY   STATUS    RESTARTS   AGE
validation-webhook-c6c6b8fbb-8fbts   1/1     Running   0          17s
```

## Testing
When deploying a simple application using the Nginx image, the request is rejected by the admission webhook due to the absence of the "deployment" label
```
kubectl create deploy nginx --image=nginx
error: failed to create deployment: admission webhook "validate.default.svc" denied the request: The label "development" isn't set!
```
```
kubectl logs -f validation-webhook-c6c6b8fbb-8fbts
[2024-04-12 06:02:35,911] ERROR in validate: Object Deployment/nginx doesn't have the required "development" label. Request rejected!
```
However, when giving the "deployment" label
```Yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: nginx
    development: test
  name: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - image: nginx
        name: nginx
```
```
kubectl apply -f label.yaml
deployment.apps/nginx created
```

## Let Validating Webhook only works on certain Namespace
Create Namespace test-ns
```bash
kubectl create namespace test-ns
```
Check Namespace labels
```bash
kubectl get namespace default --show-labels

NAME      STATUS   AGE    LABELS
test-ns   Active   104s   kubernetes.io/metadata.name=test-ns
```
Modify webhook-config.yaml
```Yaml
webhooks:
  - name: validate.default.svc
    namespaceSelector:
      matchLabels:
        kubernetes.io/metadata.name: test-ns
```
Testing
```bash
kubectl create deploy nginx --image=nginx
deployment.apps/nginx created
```

# 📌 Mutating Webhook
## Target
### Dynamically insert the ConfigMap after launching the Pod
## Create certificate
```
openssl req -x509 -sha256 -newkey rsa:2048 -keyout webhook.key -out webhook.crt -days 1024 -nodes -addext "subjectAltName = DNS.1:mutating-webhook.default.svc"
```
## Do the same steps of appling Secret, Deployment...

## Testing
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: nginx-sts
spec:
  serviceName: nginx-sts
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: nginx-ds
spec:
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment-with-label
spec:
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      nodeSelector:
        test: test
      containers:
      - name: nginx
        image: nginx:1.14.2
```

