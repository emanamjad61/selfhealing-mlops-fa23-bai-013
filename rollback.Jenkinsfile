pipeline {
    agent any

    stages {
        stage('Switch Traffic to Stable (Green)') {
            steps {
                sh '''
                    set -eux
                    sudo -u azureuser kubectl patch service sentiment-api-service -p '{"spec":{"selector":{"app":"sentiment-api","slot":"green"}}}'
                    sudo -u azureuser kubectl get service sentiment-api-service -o wide
                '''
            }
        }
    }
}
