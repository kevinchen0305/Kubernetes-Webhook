# Kubernetes Admission Webhook
Implement Kubernetes mutating webhook &amp; validating webhook

# 📌 Validating Webhook
## Create certificate
```Bash
openssl req -x509 -sha256 -newkey rsa:2048 -keyout webhook.key -out webhook.crt -days 1024 -nodes -addext "subjectAltName = DNS.1:validate.default.svc"
```

# 📌 Mutating Webhook
