// Jenkinsfile: scripted Jenkins pipefile
// This file was automatically generated using 'python -m vsc.install.ci'
// DO NOT EDIT MANUALLY

node {
    stage('checkout git') {
        checkout scm
        // remove untracked files (*.pyc for example)
        sh 'git clean -fxd'
    }
    stage ('ruff format') {
        sh 'curl -L --silent https://github.com/astral-sh/ruff/releases/download/0.13.1/ruff-x86_64-unknown-linux-gnu.tar.gz --output - | tar -xzv'
        sh 'cp ruff-x86_64-unknown-linux-gnu/ruff .'
        sh './ruff --version'
        sh './ruff format --check .'
    }
    stage ('ruff check') {
        sh 'curl -L --silent https://github.com/astral-sh/ruff/releases/download/0.13.1/ruff-x86_64-unknown-linux-gnu.tar.gz --output - | tar -xzv'
        sh 'cp ruff-x86_64-unknown-linux-gnu/ruff .'
        sh './ruff --version'
        sh './ruff check .'
    }
    stage('test') {
        sh 'pip3 install --ignore-installed --prefix $PWD/.vsc-tox tox'
        sh 'export PATH=$PWD/.vsc-tox/bin:$PATH && export PYTHONPATH=$PWD/.vsc-tox/lib/python$(python3 -c "import sys; print(\\"%s.%s\\" % sys.version_info[:2])")/site-packages:$PYTHONPATH && tox -v -c tox.ini'
        sh 'rm -r $PWD/.vsc-tox'
    }
}
