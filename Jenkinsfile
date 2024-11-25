pipeline {
    agent {
        kubernetes {
            label 'reactapp-agent'
            idleMinutes 5
            yamlFile 'jenkins-agent.yaml'
            defaultContainer 'dind'
        }            
    }

    environment {
        BACKEND_IMAGE = 'danbit2024/backend-app'
        FRONTEND_IMAGE = 'danbit2024/frontend-app'
        DOCKER_REGISTRY = 'https://registry.hub.docker.com'
        GITLAB_API_URL = 'https://gitlab.com/api/v4'
        GITLAB_TOKEN = credentials('gitlab-credentials')
        EMAIL_RECIPIENT = credentials('email-recipient')
        HELM_CHART_DIR = 'helm-reactapp'
        HELM_CHART_VERSION = '0.1.0'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: '*/1-building-application']],
                    userRemoteConfigs: [[url: 'https://gitlab.com/sela-tracks/1109/students/danielbit/final-project/application/react-app.git']]
                ])
            }
        }

        stage('Backend Tests & Build') {
            steps {
                // Use the python-test container to run tests
                container('python-test') {
                    dir('backend') {
                        script {
                            // Run Python tests
                            sh 'pip install pylint'
                            sh 'pylint app.py'
                            sh 'python -m pytest test_app.py'
                        }
                    }
                }

                // Use the dind container for Docker build and push
                container('dind') {
                    dir('backend') {
                        script {
                            // Build backend Docker image
                            def backendImage = docker.build("${BACKEND_IMAGE}:${BUILD_NUMBER}", "--no-cache .")
                            
                            // Push image if on the specific branch
                            if (env.BRANCH_NAME == '1-building-application') {
                                docker.withRegistry(DOCKER_REGISTRY, 'docker-creds') {
                                    backendImage.push()
                                    backendImage.push('v1')
                                }
                            }
                        }
                    }
                }
            }
        }

        stage('Frontend Tests & Build') {
            steps {
                // Step 1: Use the Node.js container for frontend build tasks
                container('nodejs') {
                    dir('frontend') {
                        script {
                            // Install Node.js dependencies and build the React app
                            sh 'npm install'
                            sh 'npm run build'
                        }
                    }
                }

                // Step 2: Use the dind container for Docker build and push tasks
                container('dind') {
                    dir('frontend') {
                        script {
                            // Build the frontend Docker image
                            def frontendImage = docker.build("${FRONTEND_IMAGE}:${BUILD_NUMBER}", "--no-cache .")

                            // Tag and push the image if on the correct branch
                            if (env.BRANCH_NAME == '1-building-application') {
                                docker.withRegistry(DOCKER_REGISTRY, 'docker-creds') {
                                    frontendImage.push()
                                    frontendImage.push('v1')
                                }
                            }
                        }
                    }
                }
            }
        }

        stage('Helm Chart Processing') {
            when {
                branch '1-building-application'
            }
            steps {
                container('dind') {
                    dir(HELM_CHART_DIR) {
                        script {
                            // Update chart version and app version
                            sh """
                                yq eval '.version = "${HELM_CHART_VERSION}"' -i Chart.yaml
                                yq eval '.appVersion = "${BUILD_NUMBER}"' -i Chart.yaml
                                
                                # Update image tags in values.yaml
                                yq eval '.backend.image.tag = "${BUILD_NUMBER}"' -i values.yaml
                                yq eval '.frontend.image.tag = "${BUILD_NUMBER}"' -i values.yaml
                            """

                            // Package helm chart
                            sh "helm package ."
                            
                            // Optional: Push to chart repository (example using OCI registry)
                            sh """
                                helm push \$(ls *.tgz) oci://registry-1.docker.io/danbit2024
                            """
                        }
                    }
                }
            }
        }
    }

//    post {
//        failure {
//            emailext (
//                subject: "Pipeline Failed: ${currentBuild.fullDisplayName}",
//                body: """
//                    Pipeline failure in ${env.JOB_NAME}
//                    Build Number: ${env.BUILD_NUMBER}
//                    Build URL: ${env.BUILD_URL}
//                """,
//                recipientProviders: [[$class: 'DevelopersRecipientProvider']],
//                to: "${env.EMAIL_RECIPIENT}"
//            )
//        }
//        success {
//            echo "Pipeline completed successfully!"
//        }
//        always {
//            // Replace cleanWs with deleteDir
//            deleteDir()
//        }
//    }
}
