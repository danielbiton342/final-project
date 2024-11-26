pipeline {
    agent {
        kubernetes {
            label 'dind-agent'
            yamlFile 'jenkins-agent.yaml'
        }
    }
    environment {
        VERSION = "${env.BUILD_NUMBER}"
        HELM_CHART_VERSION = "0.1.${env.BUILD_NUMBER}"
        BACKEND_IMAGE = 'danbit2024/backend-app'
        FRONTEND_IMAGE = 'danbit2024/frontend-app'
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Run Tests and Build backend Image') {
            steps {
                container('dind') {
                    script {
                        def newTag = "${VERSION}"
                        sh 'dockerd &'
                        sh 'sleep 5'
                        
                        // Build backend image
                        sh "docker build -t ${BACKEND_IMAGE}:${newTag} backend/"
                        
                        // Run tests
                        try {
                            sh "docker run --rm ${BACKEND_IMAGE}:${newTag} python -m pytest test_app.py"
                            echo 'Tests passed successfully'
                        } catch (Exception e) {
                            error 'Backend tests failed'
                        }
                    }
                }
            }
        }
        
        stage('Push BACKEND Image') {
            when {
                expression { currentBuild.resultIsBetterOrEqualTo('SUCCESS') }
            }
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
            when {
                expression { currentBuild.resultIsBetterOrEqualTo('SUCCESS') }
            }
            steps {
                script {
                    def newTag = "${VERSION}"
                    sh "sed -i 's/tag: .*/tag: \"${newTag}\"/' helm-reactapp/values.yaml"
                }
            }
        }
        
        stage('Build and push helm chart') {
            when {
                expression { currentBuild.resultIsBetterOrEqualTo('SUCCESS') }
            }
            steps {
                container('dind') {
                    script {
                        sh """
                   
                        sed -i "s/version: .*/version: ${HELM_CHART_VERSION}/" helm-reactapp/Chart.yaml

                    
                        helm package helm-reactapp

                       
                        helm push helm-reactapp-${HELM_CHART_VERSION}.tgz oci://registry-1.docker.io/danbit2024
                        """
                    }
                }
            }
        }
    }
    
    post {
        failure {
            echo 'Build failed. Check the logs for more information.'
        }
        success {
            echo 'Build completed successfully!'
        }
    }
}
