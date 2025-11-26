#!/bin/bash

if [[ $# != 1 ]]; then
    echo ''
    echo 'Usage: ./seafile-build.sh $version'
    echo ''
    exit 0
fi

version=$1
tag=v$1-server
libevhtp_tag=1.1.6
libsearpc_tag=v3.3-latest

SCRIPT=$(readlink -f "$0")
current_dir=$(dirname "${SCRIPT}")
code_path=$current_dir/src
mkdir -p ${code_path}

function install_dependencies() {
    apt-get update && apt-get upgrade -y
    apt-get install -y build-essential
    export DEBIAN_FRONTEND=noninteractive && apt-get install -y tzdata
    apt-get install -y \
        ca-certificates \
        cargo \
        cmake \
        git \
        golang-go \
        intltool \
        libarchive-dev \
        libcurl4-openssl-dev \
        libevent-dev \
        libffi-dev \
        libfuse-dev \
        libglib2.0-dev \
        libjansson-dev \
        libjpeg-dev \
        libjwt-dev \
        libldap2-dev \
        libmariadbclient-dev-compat \
        libonig-dev \
        libpq-dev \
        libsqlite3-dev \
        libssl-dev \
        libtool \
        libxml2-dev \
        libxslt-dev \
        python3 \
        python3-distro \
        python3-lxml \
        python3-ldap \
        python3-pip \
        python3-setuptools \
        python3-wheel \
        uuid-dev \
        valac \
        wget \
        curl \
        libunwind-dev \
        libhiredis-dev \
        google-perftools \
        libgoogle-perftools-dev \
        libargon2-dev
}

function install_python_dependencies() {
    cat ${code_path}/seafevents/requirements.txt ${code_path}/seafdav/requirements.txt ${code_path}/seahub/requirements.txt >${code_path}/requirements-thirdpart.txt
    cd ${code_path}

    # seafevents ignore
    sed -i 's/SQLAlchemy/# SQLAlchemy/' requirements-thirdpart.txt
    sed -i 's/mock/# mock/' requirements-thirdpart.txt
    sed -i 's/pytest/# pytest/' requirements-thirdpart.txt
    sed -i 's/gevent/# gevent/' requirements-thirdpart.txt
    sed -i 's/numpy/# numpy/' requirements-thirdpart.txt
    sed -i 's/scikit-learn/# scikit-learn/' requirements-thirdpart.txt

    # seafdav ignore
    sed -i 's/Jinja2/# Jinja2/' requirements-thirdpart.txt
    sed -i 's/sqlalchemy/# sqlalchemy/' requirements-thirdpart.txt

    # seahub ignore
    sed -i 's/django_simple_captcha/# django_simple_captcha/' requirements-thirdpart.txt
    sed -i 's/^captcha/# captcha/' requirements-thirdpart.txt
    sed -i 's/mysqlclient/# mysqlclient/' requirements-thirdpart.txt
    sed -i 's/pillow/# pillow/' requirements-thirdpart.txt
    sed -i 's/pycryptodome/# pycryptodome/' requirements-thirdpart.txt
    sed -i 's/djangosaml2/# djangosaml2/' requirements-thirdpart.txt
    sed -i 's/pysaml2/# pysaml2/' requirements-thirdpart.txt
    sed -i 's/cffi/# cffi/' requirements-thirdpart.txt
    sed -i 's/python-ldap/# python-ldap/' requirements-thirdpart.txt
    sed -i 's/PyMuPDF/# PyMuPDF/' requirements-thirdpart.txt

    # pymysql for scripts
    sed -i '$a\pymysql' requirements-thirdpart.txt
    # install
    pip3 install -r requirements-thirdpart.txt -t ${code_path}/thirdpartdir
}

function clone_code() {
    cd ${code_path}

    if [[ ! -e libevhtp ]]; then
        git clone https://github.com/haiwen/libevhtp.git
    fi

    if [[ ! -e libsearpc ]]; then
        git clone https://github.com/haiwen/libsearpc.git
    fi

    if [[ ! -e seafile-server ]]; then
        git clone https://github.com/haiwen/seafile-server.git
    fi

    if [[ ! -e seafobj ]]; then
        git clone https://github.com/haiwen/seafobj.git
    fi

    if [[ ! -e seafdav ]]; then
        git clone https://github.com/haiwen/seafdav.git
    fi

    if [[ ! -e seafevents ]]; then
        git clone https://github.com/haiwen/seafevents.git
    fi

    if [[ ! -e seahub ]]; then
        git clone https://github.com/haiwen/seahub.git
    fi
}

function fetch() {
    cd ${code_path}

    echo "Start fetch"
    echo ''

    echo "Fetch libevhtp"
    cd ${code_path}/libevhtp
    git reset --hard
    git clean -xf
    git fetch origin tag ${libevhtp_tag}
    git checkout ${libevhtp_tag}
    cd ${code_path}

    echo "Fetch libsearpc"
    cd ${code_path}/libsearpc
    git reset --hard
    git clean -xf
    git fetch origin tag ${libsearpc_tag}
    git checkout ${libsearpc_tag}
    cd ${code_path}

    echo "Fetch seafile-server"
    cd ${code_path}/seafile-server
    git reset --hard
    git clean -xf
    git fetch origin tag ${tag}
    git checkout ${tag}
    cd ${code_path}

    echo "Fetch seafobj"
    cd ${code_path}/seafobj
    git reset --hard
    git clean -xf
    git fetch origin tag ${tag}
    git checkout ${tag}
    cd ${code_path}

    echo "Fetch seafdav"
    cd ${code_path}/seafdav
    git reset --hard
    git clean -xf
    git fetch origin tag ${tag}
    git checkout ${tag}
    cd ${code_path}

    echo "Fetch seafevents"
    cd ${code_path}/seafevents
    git reset --hard
    git clean -xf
    git fetch origin tag ${tag}
    git checkout ${tag}
    cd ${code_path}

    echo "Fetch seahub"
    cd ${code_path}/seahub
    git reset --hard
    git clean -xf
    git fetch origin tag ${tag}
    git checkout ${tag}
    cd ${code_path}
}

function build() {
    cd ${current_dir}
    python3 ./seafile-build.py --version=${version} --builddir=${current_dir} --srcdir=${code_path} --thirdpartdir=${code_path}/thirdpartdir --mysql_config=/usr/bin/mariadb_config
}

echo ''
echo "Info: Seafile Version [ ${tag} ]"
echo ''

install_dependencies
wait

clone_code
wait

fetch
wait

install_python_dependencies
wait

build

echo ''
echo "Info: Successfully built seafile-server-${version}"
echo ''
