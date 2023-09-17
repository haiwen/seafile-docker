CREATE DATABASE IF NOT EXISTS seafile_dev;
CREATE DATABASE IF NOT EXISTS ccnet_dev;
CREATE DATABASE IF NOT EXISTS seahub_dev;

CREATE USER 'seafile_dev_user'@'%' IDENTIFIED BY 'pass';

GRANT ALL PRIVILEGES ON seafile_dev.* TO 'seafile_dev_user'@'%';
GRANT ALL PRIVILEGES ON ccnet_dev.* TO 'seafile_dev_user'@'%';
GRANT ALL PRIVILEGES ON seahub_dev.* TO 'seafile_dev_user'@'%';

FLUSH PRIVILEGES;

