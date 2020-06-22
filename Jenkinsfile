pipeline {
    environment {
        // This registry is important for removing the image after the tests
        registry = "cv2tools"
    }
    agent any
    stages {
        stage("Test") {
            steps {
                script {
                    // Building the Docker image
                    dockerImage = docker.build registry + ":$BUILD_NUMBER"

                    try {
                        dockerImage.inside() {
                            // Extracting the PROJECTDIR environment variable from inside the container
                            def PROJECTDIR = sh(script: 'echo \$PROJECTDIR', returnStdout: true).trim()

                            // Copying the project tests into our workspace
                            sh "cp -r '$PROJECTDIR/test' '$WORKSPACE'"

                            // Running the tests inside the new directory
                            dir("$WORKSPACE/test") {
                                sh "-m unittest discover"
                            }
                        }

                    } finally {
                        // Removing the docker image
                        sh "docker rmi $registry:$BUILD_NUMBER"
                    }
                }
            }
        }
    }
}