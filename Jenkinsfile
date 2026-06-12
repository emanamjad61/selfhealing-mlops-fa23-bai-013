pipeline {
    agent any

    environment {
        DOCKERHUB_USER = 'catmommy'
        IMAGE_NAME = 'sentiment-api'
        BASE_URL = 'http://sentiment-test-app:5000'
    }

    stages {
        stage('Fetch') {
            steps {
                checkout scm
            }
        }

        stage('Build and Run') {
            steps {
                sh '''
                    set -eux
                    docker rm -f sentiment-test-app || true
                    docker network inspect sentiment-ci >/dev/null 2>&1 || docker network create sentiment-ci
                    docker build -t ${DOCKERHUB_USER}/${IMAGE_NAME}:unstable .
                    docker run -d --name sentiment-test-app --network sentiment-ci -p 5000:5000 ${DOCKERHUB_USER}/${IMAGE_NAME}:unstable
                    for i in $(seq 1 90); do
                        if docker run --rm --network sentiment-ci curlimages/curl:8.8.0 -fsS http://sentiment-test-app:5000/health; then
                            exit 0
                        fi
                        sleep 2
                    done
                    docker logs sentiment-test-app
                    exit 1
                '''
            }
        }

        stage('Unit Test') {
            steps {
                sh '''
                    set -eux
                    docker run --rm --network sentiment-ci \
                        -e BASE_URL=${BASE_URL} \
                        ${DOCKERHUB_USER}/${IMAGE_NAME}:unstable \
                        pytest -q tests/test_api.py
                '''
            }
        }

        stage('UI Test') {
            steps {
                sh '''
                    set -eux
                    docker run --rm --network sentiment-ci \
                        -e BASE_URL=${BASE_URL} \
                        ${DOCKERHUB_USER}/${IMAGE_NAME}:unstable \
                        pytest -q tests/test_ui.py
                '''
            }
        }

        stage('Build and Push') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_TOKEN')]) {
                    sh '''
                        set -eux
                        echo "$DOCKER_TOKEN" | docker login -u "$DOCKER_USER" --password-stdin
                        docker build -t ${DOCKERHUB_USER}/${IMAGE_NAME}:unstable .
                        tmpdir=$(mktemp -d)
                        git clone --depth 1 --branch stable-fallback https://github.com/emanamjad61/selfhealing-mlops-fa23-bai-013.git "$tmpdir"
                        docker build -t ${DOCKERHUB_USER}/${IMAGE_NAME}:stable "$tmpdir"
                        docker push ${DOCKERHUB_USER}/${IMAGE_NAME}:unstable
                        docker push ${DOCKERHUB_USER}/${IMAGE_NAME}:stable
                        rm -rf "$tmpdir"
                    '''
                }
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh '''
                    set -eux
                    kubectl apply -f k8s/pvc.yaml
                    kubectl apply -f k8s/blue-deployment.yaml
                    kubectl apply -f k8s/green-deployment.yaml
                    kubectl apply -f k8s/service.yaml
                    kubectl rollout status deployment/sentiment-blue-deployment --timeout=300s
                    kubectl rollout status deployment/sentiment-green-deployment --timeout=300s
                '''
            }
        }
    }

    post {
        always {
            sh 'docker rm -f sentiment-test-app || true'
        }
    }
}
