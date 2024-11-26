pipeline {
    agent {
        kubernetes {
            label 'dind-agent'
            yamlFile 'jenkins-agent.yaml'
        }
    }
    environment {
        VERSION = "${env.BUILD_NUMBER}"
        BACKEND_IMAGE = 'danbit2024/backend-app'
        FRONTEND_IMAGE = 'danbit2024/frontend-app'


    }
    stages {
        stage('Run Tests and Build backend Image') {
            steps {
                container('dind') {
                    script {
                        def newTag = "${VERSION}"
                        sh 'dockerd &'
                        sh 'sleep 5'
                        sh "docker build -t ${BACKEND_IMAGE}:${newTag} ."
                        sh "docker run ${BACKEND_IMAGE}:${newTag} test_app.py"
                        echo 'passed test'
                    }
                }
            }
        }
        stage('Push BACKEND Image') {
            steps {
                container('dind') {
                    script {
                        def newTag = "${VERSION}"
                        withCredentials([usernamePassword(credentialsId: 'docker-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                            sh """
                            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                            docker push ${BACKEND_IMAGE}:${newTag}
                            """
                        }
                    }
                }
            }
        }
        stage('Update Helm Values and Commit Changes') {
            steps {
                script {
                    def newTag = "${VERSION}"
                    sh "sed -i 's/tag: .*/tag: \"${newTag}\"/' helm-reactapp/values.yaml"
                }
            }
        }
        stage('Build and push helm chart') {
            steps {
                container('dind') {
                    script {
                        def newTag = "${VERSION}"
                        withCredentials([usernamePassword(credentialsId: 'docker-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                            sh """
                            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                            helm package helm-reactapp
                            helm push helm-reactapp-0.5.0.tgz oci://registry-1.docker.io/danbit2024
                            """
                        }
                    }
                }
            }
        }
    }
}