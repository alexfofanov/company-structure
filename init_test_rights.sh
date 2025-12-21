#!/bin/bash
set -e

echo "Granting creating databases privileges to user '$MARIADB_USER'"

mariadb -u root -p"$MARIADB_ROOT_PASSWORD" <<-EOSQL
    GRANT ALL PRIVILEGES ON \`test_%\`.* TO '$MARIADB_USER'@'%';
    FLUSH PRIVILEGES;
EOSQL