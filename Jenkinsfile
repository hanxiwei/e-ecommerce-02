pipeline {
    agent any

    parameters {
        choice(name: 'TEST_SUITE', choices: ['smoke', 'regression', 'ui', 'all'], description: 'Select test suite')
    }

    stages {
        stage('Docker Access Check') {
            steps {
                script {
                    def dockerOk = sh(returnStatus: true, script: 'docker ps > /dev/null 2>&1') == 0
                    if (!dockerOk) {
                        error('Jenkins cannot access Docker daemon (docker.sock). Fix Docker socket permission or Jenkins container Docker integration, then rerun.')
                    }
                }
            }
        }

        stage('Build Image') {
            steps {
                script {
                    def compose = { String args ->
                        sh """if command -v docker-compose >/dev/null 2>&1; then
  docker-compose ${args}
else
  docker compose ${args}
fi"""
                    }

                    def shortSha = (env.GIT_COMMIT != null && env.GIT_COMMIT.trim()) ? env.GIT_COMMIT.take(7) : "build${env.BUILD_NUMBER}"
                    env.API_IMAGE = "e-ecommerce-01-api:${shortSha}"
                    env.COMPOSE_PROJECT = "ecom-${env.BUILD_NUMBER}-${shortSha}"

                    def n = 0
                    try { n = Integer.parseInt(env.BUILD_NUMBER ?: "0") } catch (ignored) { n = 0 }
                    env.API_PORT = String.valueOf(18000 + (n % 1000))
                    env.DB_PORT = String.valueOf(15432 + (n % 1000))

                    sh "docker build -t ${env.API_IMAGE} ."
                }
            }
        }

        stage('Start Ephemeral Env') {
            steps {
                script {
                    def compose = { String args ->
                        sh """if command -v docker-compose >/dev/null 2>&1; then
  docker-compose ${args}
else
  docker compose ${args}
fi"""
                    }

                    withEnv([
                        "API_IMAGE=${env.API_IMAGE}",
                        "API_PORT=${env.API_PORT}",
                        "DB_PORT=${env.DB_PORT}",
                        "DATABASE_URL=postgresql://postgres:password@db:5432/ecommercedb",
                        "SECRET_KEY=dev-secret",
                        "ALGORITHM=HS256",
                        "ACCESS_TOKEN_EXPIRE_MINUTES=30",
                    ]) {
                        compose("-p ${env.COMPOSE_PROJECT} up -d --no-build")
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    def compose = { String args ->
                        sh """if command -v docker-compose >/dev/null 2>&1; then
  docker-compose ${args}
else
  docker compose ${args}
fi"""
                    }

                    def markerExpr = ''
                    if (params.TEST_SUITE != null && params.TEST_SUITE != 'all') {
                        markerExpr = "-m ${params.TEST_SUITE}"
                    }

                    withEnv([
                        "API_IMAGE=${env.API_IMAGE}",
                        "API_PORT=${env.API_PORT}",
                        "DB_PORT=${env.DB_PORT}",
                        "DATABASE_URL=postgresql://postgres:password@db:5432/ecommercedb",
                        "SECRET_KEY=dev-secret",
                        "ALGORITHM=HS256",
                        "ACCESS_TOKEN_EXPIRE_MINUTES=30",
                    ]) {
                        compose("-p ${env.COMPOSE_PROJECT} exec -T api rm -rf /app/allure-results || true")
                        def testExit = sh(returnStatus: true, script: """if command -v docker-compose >/dev/null 2>&1; then
  docker-compose -p ${env.COMPOSE_PROJECT} exec -T api mkdir -p /app/allure-results
  docker-compose -p ${env.COMPOSE_PROJECT} exec -T api python -m pytest tests/ ${markerExpr} --alluredir=/app/allure-results || true
else
  docker compose -p ${env.COMPOSE_PROJECT} exec -T api mkdir -p /app/allure-results
  docker compose -p ${env.COMPOSE_PROJECT} exec -T api python -m pytest tests/ ${markerExpr} --alluredir=/app/allure-results || true
fi""")

                        def apiCid = sh(returnStdout: true, script: """if command -v docker-compose >/dev/null 2>&1; then
  docker-compose -p ${env.COMPOSE_PROJECT} ps -q api
else
  docker compose -p ${env.COMPOSE_PROJECT} ps -q api
fi""").trim()
                        sh 'rm -rf ./allure-results || true'
                        sh "docker cp ${apiCid}:/app/allure-results ./allure-results"
                        sh 'chmod -R 777 allure-results || true'

                        if (testExit != 0) {
                            currentBuild.result = 'FAILURE'
                            error("pytest failed with exit code: ${testExit}")
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                def compose = { String args ->
                    sh """if command -v docker-compose >/dev/null 2>&1; then
  docker-compose ${args}
else
  docker compose ${args}
fi"""
                }

                sh 'rm -rf ./allure-report || true'
                allure includeProperties: false, jdk: '', results: [[path: 'allure-results']]
                archiveArtifacts artifacts: 'allure-results/**', allowEmptyArchive: true
                if (env.COMPOSE_PROJECT != null && env.COMPOSE_PROJECT.trim()) {
                    compose("-p ${env.COMPOSE_PROJECT} down -v --remove-orphans || true")
                }
                if (env.API_IMAGE != null && env.API_IMAGE.trim()) {
                    sh "docker rmi ${env.API_IMAGE} || true"
                }
            }
        }
    }
}
