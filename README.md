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

# 📌 Mutating Webhook
