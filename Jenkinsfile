// Jenkinsfile: scripted Jenkins pipefile
// This file was automatically generated using 'python -m vsc.install.ci'
// DO NOT EDIT MANUALLY

node {
    stage('checkout git') {
        checkout scm
        // remove untracked files (*.pyc for example)
        sh 'git clean -fxd'
    }
    stage('test') {
        sh 'python2.7 -V'
        sh 'pip3 install --ignore-installed --user tox'
        sh 'export PATH=$HOME/.local/bin:$PATH && tox -v -c tox.ini'
    }
}
