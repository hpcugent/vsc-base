#!/usr/bin/env groovy
 
node {
    stage 'Checkout'
    checkout scm
    stage 'install dependencies'
    sh "wget -O ez_setup.py https://bootstrap.pypa.io/ez_setup.py"
    sh "python ez_setup.py --user"
    sh "python -m easy_install -U --user vsc-install"
    stage 'cleanup'
    sh "git clean -fd"
    stage 'test'
    sh "python setup.py test"
}
