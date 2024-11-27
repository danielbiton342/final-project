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
        VALUES_FILE = "helm-reactapp/values.yaml"
        APPLICATION_FILE = "cicd/application.yaml"
    }
    stages {
        stage('Checkout code') {
            steps {
                script {
                    checkout scm: [
                        $class: 'GitSCM', 
                        branches: [[name: '*/1-building-application']], 
                        userRemoteConfigs: scm.userRemoteConfigs
                    ]
                    sh "git config --global --add safe.directory ${env.WORKSPACE}"
                    checkout scm
                    def commitMessage = sh(
                        script: "git log -1 --pretty=%B",
                        returnStdout: true
                    ).trim()

                    if (commitMessage.contains("[skip-ci]")) {
                        echo "Skipping build due to commit message: ${commitMessage}"
                        error("Build aborted due to [skip-ci] in commit message.")
                    }
                    
                    echo "Proceeding with build. Commit message: ${commitMessage}"
                }
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

                        // Run pylint and capture the exit code
                        def pylintExitCode = sh(
                            script: "docker run --rm ${BACKEND_IMAGE}:${newTag} pylint /app/app.py",
                            returnStatus: true
                        )

                        // Print the pylint score
                        sh "docker run --rm ${BACKEND_IMAGE}:${newTag} pylint /app/app.py | grep 'Your code has been rated at'"

                        // Optionally, you can add a warning if the score is below a certain threshold
                        if (pylintExitCode != 0) {
                            echo "WARNING: Pylint found issues with the code. Please review the code quality."
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
        
        stage('Run Tests and Build Frontend Image') {
            steps{
                container('dind') {
                    script {
                        def newTag = "${VERSION}"
                        sh 'dockerd &'
                        sh 'sleep 5'

                        // Build frontend image
                        sh "docker build -t ${FRONTEND_IMAGE}:${newTag} frontend/"

                        script: "docker run --rm ${FRONTEND_IMAGE}:${newTag}"
                    }
                }
            }
        }
        stage('Push Frontend Image') {
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
                            docker push ${FRONTEND_IMAGE}:${newTag}
                            """
                        }
                    }
                }
            }
        }
        stage('Update Helm Values') {
            when {
                expression { currentBuild.resultIsBetterOrEqualTo('SUCCESS') }
            }
            steps {
                script {
                    sh 'sed -i "s|tag: .*|tag: ${BUILD_NUMBER}|" "${VALUES_FILE}"'
                    sh  'echo "Updated tag to ${BUILD_NUMBER}"'

                }
            }
        }
        
        stage('Commit and Push Updated Values') {
            when {
                expression { currentBuild.resultIsBetterOrEqualTo('SUCCESS') }
            }
            steps {
                script {
                    // Use the GitLab token for authentication
                    withCredentials([string(credentialsId: 'gitlab-token', variable: 'GITLAB_TOKEN')]) {                      
                        sh """
                        git config --global user.name "jenkins-ci"
                        git config --global user.email "jenkins@ci.com"
                       git remote set-url origin https://oauth2:${GITLAB_TOKEN}@gitlab.com/sela-tracks/1109/students/danielbit/final-project/application/react-app.git
                        git add ${VALUES_FILE}
                        git commit -m "Update helm chart tag to ${BUILD_NUMBER}"
                        git push origin 1-building-application
                        """
                    }
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

                        sed -i "s|targetRevision: .*|targetRevision: ${BUILD_NUMBER}|" "${APPLICATION_FILE}"
                        """
                    }
                }
            }
        }
    }
    
    post {
        success {
            script {
               
                withCredentials([string(credentialsId: 'gitlab-token', variable: 'GITLAB_TOKEN')]) {
                    def projectId = '64685307'
                    def sourceBranch = '1-building-application'
                    def targetBranch = 'main'

                    sh """
                    curl --request POST \
                         --header "PRIVATE-TOKEN: ${GITLAB_TOKEN}" \
                         --header "Content-Type: application/json" \
                         --data '{
                             "source_branch": "${sourceBranch}",
                             "target_branch": "${targetBranch}",
                             "title": "Merge ${sourceBranch} into ${targetBranch} invoked by jenkins CI",
                             "description": "Merge request created automatically by Jenkins CI pipeline."
                         }' \
                         "https://gitlab.com/api/v4/projects/${projectId}/merge_requests"
                    """
                }
            }
            echo 'Build completed successfully!'
        }

        failure {
            emailext subject: '$DEFAULT_SUBJECT', 
                     body: '$DEFAULT_CONTENT', 
                     recipientProviders: [ 
                         [$class: 'CulpritsRecipientProvider'], 
                         [$class: 'DevelopersRecipientProvider'], 
                         [$class: 'RequesterRecipientProvider'] 
                     ], 
                     replyTo: '$DEFAULT_REPLYTO', 
                     to: '$DEFAULT_RECIPIENTS'
            echo 'Build failed. Check the logs for more information.'
        }
    }
}