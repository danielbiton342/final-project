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
        DEPLOY_BRANCH = '1-building-application'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: "*/${env.DEPLOY_BRANCH}"]],
                    userRemoteConfigs: [[url: 'https://gitlab.com/sela-tracks/1109/students/danielbit/final-project/application/react-app.git']]
                ])
            }
        }

        stage('Backend Tests & Build') {
            steps {
                container('python-test') {
                    dir('backend') {
                        script {
                            try {
                                sh '''
                                    pip install -r requirements.txt
                                    pip install pylint pytest
                                    pylint app.py
                                    python -m pytest test_app.py
                                '''
                            } catch (Exception e) {
                                error "Backend tests failed: ${e.message}"
                            }
                        }
                    }
                }

                container('dind') {
                    dir('backend') {
                        script {
                            def backendImage = docker.build("${BACKEND_IMAGE}:${BUILD_NUMBER}", "--no-cache .")
                            
                            if (env.BRANCH_NAME == env.DEPLOY_BRANCH) {
                                docker.withRegistry(DOCKER_REGISTRY, 'docker-creds') {
                                    backendImage.push()
                                    backendImage.push('latest')
                                }
                            }
                        }
                    }
                }
            }
        }

        stage('Frontend Tests & Build') {
            steps {
                container('nodejs') {
                    dir('frontend') {
                        script {
                            try {
                                sh '''
                                    npm ci
                                    npm run test -- --watchAll=false
                                    npm run build
                                '''
                            } catch (Exception e) {
                                error "Frontend build failed: ${e.message}"
                            }
                        }
                    }
                }

                container('dind') {
                    dir('frontend') {
                        script {
                            def frontendImage = docker.build("${FRONTEND_IMAGE}:${BUILD_NUMBER}", "--no-cache .")

                            if (env.BRANCH_NAME == env.DEPLOY_BRANCH) {
                                docker.withRegistry(DOCKER_REGISTRY, 'docker-creds') {
                                    frontendImage.push()
                                    frontendImage.push('latest')
                                }
                            }
                        }
                    }
                }
            }
        }

        stage('Helm Chart Processing') {
            when {
                expression { env.BRANCH_NAME == env.DEPLOY_BRANCH }
            }
            steps {
                container('dind') {
                    dir(HELM_CHART_DIR) {
                        script {
                            try {
                                sh """
                                    yq eval '.version = "${HELM_CHART_VERSION}"' -i Chart.yaml
                                    yq eval '.appVersion = "${BUILD_NUMBER}"' -i Chart.yaml
                                    
                                    yq eval '.backend.image.tag = "${BUILD_NUMBER}"' -i values.yaml
                                    yq eval '.frontend.image.tag = "${BUILD_NUMBER}"' -i values.yaml
                                    
                                    helm lint .
                                    helm package .
                                    helm push \$(ls *.tgz) oci://registry-1.docker.io/danbit2024
                                """
                            } catch (Exception e) {
                                error "Helm chart processing failed: ${e.message}"
                            }
                        }
                    }
                }
            }
        }
    }

    post {
        failure {
            emailext (
                subject: "Pipeline Failed: ${currentBuild.fullDisplayName}",
                body: """
                    Pipeline failure in ${env.JOB_NAME}
                    Build Number: ${env.BUILD_NUMBER}
                    Build URL: ${env.BUILD_URL}
                """,
                recipientProviders: [[$class: 'DevelopersRecipientProvider']],
                to: "${env.EMAIL_RECIPIENT}"
            )
        }
        success {
            echo "Pipeline completed successfully!"
        }
        always {
            deleteDir()
        }
    }
}