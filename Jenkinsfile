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

    stage('Build docs') {
        sh "docker run --rm \$(echo ${env.BUILD_TAG} | tr '[A-Z]' '[a-z]' | tr -cd '[a-z0-9\n]') make html"
    }

    if (env.BRANCH_NAME == "master") {
        stage('Publish') {
            dir("core") {
                sh "sp-pypi-upload"
            }
            dir("google") {
                sh "sp-pypi-upload"
            }
        }
    }
}
