# React Application

## Table of Contents

- [React Application](#react-application)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Brief Explanation About The React App](#brief-explanation-about-the-react-app)
  - [Setting Up the Application on Kubernetes Cluster](#setting-up-the-application-on-kubernetes-cluster)
    - [Setting the MusicDB Password](#setting-the-musicdb-password)
    - [Making the Script Executable](#making-the-script-executable)
    - [Verify the Helm installation worked as expected](#verify-the-helm-installation-worked-as-expected)
    - [Checking the website application](#checking-the-website-application)
  - [Troubleshooting](#troubleshooting)
  - [Cleanup](#cleanup)
    - [1. Uninstall the Helm Release](#1-uninstall-the-helm-release)
    - [2. Uninstall the deployment namespace](#2-uninstall-the-deployment-namespace)

## Prerequisites

Before setting up the application, ensure you have the following prerequisites:

- **Kubernetes Cluster**: A running Kubernetes cluster. If you're using a local setup, Docker Desktop with Kubernetes or Minikube should suffice.
- **Helm CLI**: Install Helm for managing Kubernetes applications. Follow the [Helm installation guide](https://helm.sh/docs/intro/install/).
- **MongoDB Setup**: MongoDB should be set up and accessible to the application. For detailed setup instructions, refer to the [MongoDB setup guide](https://gitlab.com/sela-tracks/1109/students/danielbit/final-project/infrastructure/mongodb).

## Brief Explanation About The React App
This application is a microservice app, it has a frontend that is built on react .jsx, and a backend which is an api server that is written in python.
This Application is a simple singers/songs management application that let the user to add/delete singers or songs for his list.

This React application is designed to work with MongoDB.
The application is containerized using Docker and deployed to a Kubernetes cluster for scalability and ease of management. 

## Setting Up the Application on Kubernetes Cluster

Follow these steps to set up and deploy the React application on your Kubernetes cluster.

### Setting the MusicDB Password

**Set the environment variable for the MongoDB password**

Replace `your_secure_password_here` with a strong, secure password.

  ```bash
   export BACKEND_APP_PASSWORD="your_secure_password_here"
  ```

### Making the Script Executable

Ensure that the MongoDB setup script is executable:

```bash
chmod +x ./setup-mongodb.sh
```
 **Run the script to configure MongoDB with the proper settings.**

```bash
./setup-mongodb.sh
```
Verify MongoDB Secret Creation
To confirm the secret has been created, check the mongodb-secret:

```bash
kubectl get secret mongodb-secret -n deployment -o yaml
```

**Deploy React Application Using Helm**

First pull the right version of the helm chart:

```bash
helm pull oci://registry-1.docker.io/danbit2024/helm-reactapp --version 0.1.0 -n deployment
```
Then install it in deployment namespace using the following command:
```bash
helm install my-react-app oci://registry-1.docker.io/danbit2024/helm-reactapp --version 0.1.0 -n deployment
```
The command has deployed the application to the Kubernetes cluster using a Helm chart with the version 0.1.0 


### Verify the Helm installation worked as expected
Run the following command to inspect the deployment namespace:
```bash
kubectl get all -n deployment
```

### Checking the website application
The application is running on port 30000 since it's being exposed by a nodePort type service, visit the following URL:
```bash
http://localhost:30000
```
You should see the following home page:
![homepage](./homepage.png)



## Troubleshooting
If you run into any issues during setup or deployment, here are a few tips:

Check Kubernetes pods status: If the React application doesn't start, check the status of the pods:

```bash
kubectl get pods -n deployment
kubectl log <pod name> -n deployment
```

Check Helm release status: To ensure the Helm deployment was successful, use:

```bash
helm status helm-reactapp -n deployment
```
MongoDB connection issues: If the React app cannot connect to MongoDB, verify that the MongoDB pod is running and the connection string is correct in your environment settings.




## Cleanup

Follow these steps in order to clean up all resources created during the setup process:

### 1. Uninstall the Helm Release
Remove the React application deployment:
```bash
helm uninstall my-react-app -n deployment
```

### 2. Uninstall the deployment namespace
Remove all the resources inside deployment namespace including the namespace itself (use this command only if you don't need anything inside the deployment namespace)
```bash
kubectl delete namespace deployment
```
