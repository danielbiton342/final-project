#!/bin/bash

# Retrieve MongoDB root password
NAMESPACE="mongodb"
SECRET_NAME="my-mongodb"
ROOT_PASSWORD=$(kubectl get secret --namespace "$NAMESPACE" "$SECRET_NAME" -o jsonpath="{.data.mongodb-root-password}" | base64 --decode)

# Define database, role, and user details
DB_NAME="musicDB"
ROLE_NAME="backendRole"
USER_NAME="backendAppUser"
USER_PASSWORD="${BACKEND_APP_PASSWORD}"

if [ -z "$USER_PASSWORD" ]; then
  echo "Error: BACKEND_APP_PASSWORD is not set. Export it using: export BACKEND_APP_PASSWORD=<password>"
  exit 1
fi

# Delete the existing job if it exists
kubectl delete job mongodb-init-job --namespace $NAMESPACE --ignore-not-found=true

# Create a Kubernetes Job for MongoDB initialization
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: Job
metadata:
  name: mongodb-init-job
  namespace: $NAMESPACE
spec:
  backoffLimit: 2
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: mongo-init
        image: mongo
        command: ["mongosh"]
        args:
          - "mongodb://root:$ROOT_PASSWORD@my-mongodb.mongodb.svc.cluster.local:27017/admin"
          - "--eval"
          - |
            // Create the role
            db.getSiblingDB("$DB_NAME").createRole({
                role: "$ROLE_NAME",
                privileges: [
                    { resource: { db: "$DB_NAME", collection: "" }, actions: ["find", "insert", "update", "remove", "createCollection", "createIndex", "dropIndex"] }
                ],
                roles: []
            });

            // Create the user and assign the new role
            db.getSiblingDB("$DB_NAME").createUser({
                user: "$USER_NAME",
                pwd: "$USER_PASSWORD",
                roles: [{ role: "$ROLE_NAME", db: "$DB_NAME" }]
            });

            print("Role and user created successfully.");
EOF

# Wait for the job to complete and get the pod name
echo "Waiting for the MongoDB initialization job to complete..."

POD_NAME=$(kubectl get pods --namespace $NAMESPACE --selector=job-name=mongodb-init-job -o jsonpath='{.items[0].metadata.name}')

if [ -z "$POD_NAME" ]; then
  echo "Error: MongoDB initialization pod not found!"
  exit 1
fi

# Wait for the pod to complete
kubectl wait --for=condition=complete pod/$POD_NAME --namespace $NAMESPACE --timeout=60s

# Display logs for debugging if the pod fails
JOB_STATUS=$(kubectl get pod $POD_NAME --namespace $NAMESPACE -o jsonpath='{.status.containerStatuses[0].state.terminated.exitCode}')

if [ "$JOB_STATUS" != "0" ]; then
  echo "MongoDB initialization job failed. Fetching logs..."
  kubectl logs $POD_NAME --namespace $NAMESPACE
  exit 1
fi

# Clean up the Job after successful execution
kubectl delete job mongodb-init-job --namespace $NAMESPACE
echo "MongoDB initialization completed successfully."
