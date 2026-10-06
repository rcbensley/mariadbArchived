gen_cert() {
    if [[ -z $1 ]]; then exit "Missing name"; fi
    openssl genrsa -out ${1}-ca-key.pem 4096
    openssl req -new -x509 -nodes -key ${1}-ca-key.pem -sha256 -out ${1}-ca-cert.pem
}

gen_server() {
    if [[ -z $1 ]]; then exit "Missing name"; fi
    openssl genrsa -out ${1}-server-key.pem 4096
    openssl req -new -key ${1}-server-key.pem -out ${1}-server-csr.pem
    openssl x509 -req -in ${1}-server-csr.pem -CA ${1}-ca-cert.pem -CAkey ${1}-ca-key.pem -CAcreateserial -out ${1}-server-cert.pem -days 365 -sha256
}

gen_client() {
    if [[ -z $1 ]]; then exit "Missing name"; fi
    openssl genrsa -out ${1}-client-key.pem 4096
    openssl req -new -key ${1}-client-key.pem -out ${1}-client-csr.pem
    openssl x509 -req -in ${1}-client-csr.pem -CA ${1}-ca-cert.pem -CAkey ${1}-ca-key.pem -CAcreateserial -out ${1}-client-cert.pem -days 365 -sha256
}

gen_change_master() {
    if [[ -z $1 ]]; then exit "Missing name"; fi
    if [[ -z $2 ]]; then exit "Missing directory"; fi
    echo "CHANGE MASTER TO
MASTER_HOST='',
MASTER_USER='',
MASTER_PASSWORD='',
MASTER_SSL=1,
MASTER_SSL_CA='${2}/${1}-ca-cert.pem',
MASTER_SSL_CERT='${2}/${1}-client-cert.pem',
MASTER_SSL_KEY='${2}/${1}-client-key.pem';
"
}

gen_cnf() {
    if [[ -z $1 ]]; then exit "Missing name"; fi
    if [[ -z $2 ]]; then exit "Missing directory"; fi
    echo "[mariadbd]
ssl-ca/ca-cert.pem
ssl-cert==${2}/${1}-server-cert.pem
ssl-key=${2}/${1}-server-key.pem
#wsrep_provider_options='socket.ssl_cert=/etc/my.cnf.d/certificates/server-cert.pem;socket.ssl_key=/etc/my.cnf.d/certificates/server-key.pem;socket.ssl_ca=/etc/my.cnf.d/certificates/ca.pem'
"
}
