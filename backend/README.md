**get hold of the password to the db admin
kubectl get secret --namespace mongodb my-mongodb -o jsonpath="{.data.mongodb-root-password}" | base64 --decode


**temporary connect to the database with your credentials to assign a new role with permissions

kubectl run mongodb-test --rm -it --image=mongo --restart=Never -- mongosh "mongodb://root:(the password retrieved)@my-mongodb.mongodb.svc.cluster.local:27017/admin"

** create new db musicDB

use musicDB

**create role for the new musicDB 

db.createRole({
  role: "backendRole",
  privileges: [
    { resource: { db: "musicDB", collection: "" }, actions: ["find", "insert", "update", "remove", "createCollection", "createIndex", "dropIndex"] }
  ],
  roles: []
});

** create a user and assign it to the musicDB

db.createUser({
  user: "backendAppUser",
  pwd: "mypassword",
  roles: [{ role: "backendRole", db: "musicDB" }]
});


kubectl create ns deployment


** create a secret of the mongoDB URI for the backend connection

kubectl create secret generic mongodb-secret \
  --namespace deployment \
  --from-literal=MONGO_URI="mongodb://backendAppUser:mypassword@my-mongodb.mongodb.svc.cluster.local:27017/musicDB"
 
 ** verify it's created
 kubectl get secret mongodb-secret -n deployment -o yaml


kubectl get secret my-mongodb-secret -n mongodb -o yaml | sed 's/namespace: mongodb/namespace: backend/' | kubectl create -f -

helm upgrade --install backend-app-v1 . --namespace deployment
