node {
    stage('Checkout') {
         checkout scm
    }

    stage('Build image') {
        sh "docker build -t \$(echo ${env.BUILD_TAG} | tr '[A-Z]' '[a-z]' | tr -cd '[a-z0-9\n]') ."
    }

    stage('Run tests') {
        sh "docker run --rm \$(echo ${env.BUILD_TAG} | tr '[A-Z]' '[a-z]' | tr -cd '[a-z0-9\n]') make tests"
    }

    stage('Build and publish docs') {
        sh """
            docker run --rm \$(echo ${env.BUILD_TAG} | tr '[A-Z]' '[a-z]' | tr -cd '[a-z0-9\n]') bash -c '
            make docs && \
            cd docs/_build/html/ && \
            zip -r docs.zip * && \
            curl -X POST -F filedata=@docs.zip -F name="docker_interface" -F version="${env.BRANCH_NAME}" -F description="Declarative interface for building images and running commands in containers using Docker." http://sonalytic-docs.spotify.net/hmfd'
            """
    }

    if (env.BRANCH_NAME == "master") {
        stage('Publish') {
            sh "sp-pypi-upload"
            sh "docker run --rm python:3 pip install docker-interface -i https://artifactory.spotify.net/artifactory/api/pypi/pypi/simple/"
        }
    }
}
