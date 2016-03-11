python 3.3+ (for flask)

flask version 0.10.1
junja2 version 2.7.3

apt-get update
sudo apt-get install build-essential
apt-get install python-dev


-if don't have python 3.3+ in repos, install manually

wget --no-check-certificate  https://www.python.org/ftp/python/3.4.3/Python-3.4.3.tgz


tar -zxvf Python-3.4.3.tgz
cd Python-3.4.3
./configure --with-zlib
make
make install

sudo mkdir -p /var/www/pymultimonit

cd /var/www/pymultimonit

pyvenv-3.4 pymultimonitvenv
. pymultimonitvenv/bin/activate



pip install --upgrade pip

pip install flask
pip install uwsgi


cp -R /root/PyMonit/* /var/www/pymultimonit/

sudo chown -R www-data:www-data /var/www/pymultimonit

-if nginx is not installed:
sudo apt-get install nginx


nano /var/www/pymultimonit/pymultimonit_nginx.conf

server {
    listen      8080;
    server_name localhost;
    charset     utf-8;
    client_max_body_size 75M;

    location / { try_files $uri @pymultimonit; }
    location @pymultimonit {
        include uwsgi_params;
        uwsgi_pass unix:/var/www/pymultimonit/pymultimonit_uwsgi.sock;
    }
}



sudo ln -s /var/www/pymultimonit/pymultimonit_nginx.conf /etc/nginx/conf.d/
sudo /etc/init.d/nginx restart


nano /var/www/pymultimonit/pymultimonit_uwsgi.ini

[uwsgi]
-application's base folder
base = /var/www/pymultimonit

-python module to import #name of python file
app = main
module = %(app)

home = %(base)/pymultimonitvenv
pythonpath = %(base)

-socket file's location
socket = /var/www/pymultimonit/%n.sock

-permissions for the socket file
chmod-socket    = 666

-the variable that holds a flask application inside the module imported at line #6
callable = app

-location of log files
logto = /var/log/uwsgi/%n.log



mkdir /var/log/uwsgi
sudo chown -R www-data:www-data /var/log/uwsgi



uwsgi --ini /var/www/pymultimonit/pymultimonit_uwsgi.ini

-TEst app, make sure it works


uwsgi --emperor "/var/www/pymultimonit/pymultimonit_uwsgi.ini"


-TEst app again, make sure it works


create the directories:
mkdir -p /etc/uwsgi/apps-enabled
mkdir -p /etc/uwsgi/apps-available

ln -s /var/www/pymultimonit/pymultimonit_uwsgi.ini /etc/uwsgi/apps-enabled



-now we will create an init script so it starts on boot

nano /etc/init.d/emperor
```bash
#!/usr/bin/env bash
 
### BEGIN INIT INFO
# Provides:          emperor
# Required-Start:    $all
# Required-Stop:     $all
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts the uwsgi emperor app server
# Description:       starts uwsgi emperor app server using start-stop-daemon
### END INIT INFO
set -e
 
 
PATH=/sbin:/bin:/usr/sbin:/usr/bin:/var/www/pymultimonit/pymultimonitvenv/bin
DAEMON=/var/www/pymultimonit/pymultimonitvenv/bin/uwsgi
RUN=/var/run/uwsgi
ENABLED_CONFIGS_DIR=/etc/uwsgi/apps-enabled
AVAILABLE_CONFIGS_DIR=/etc/uwsgi/apps-available
NAME=uwsgi
DESC=emperor
OWNER=www-data
GROUP=www-data
OP=$1
 
[[ -x $DAEMON ]] || exit 0
[[ -d $RUN ]] || mkdir $RUN && chown $OWNER.$GROUP $RUN
 
DAEMON_OPTS=""
 
# Include uwsgi defaults if available
if [[ -f /etc/default/uwsgi ]]; then
    . /etc/default/uwsgi
fi
 
do_pid_check()
{
    local PIDFILE=$1
    [[ -f $PIDFILE ]] || return 0
    local PID=$(cat $PIDFILE)
    for p in $(pgrep $NAME); do
        [[ $p == $PID ]] && return 1
    done
    return 0
}
 
 
do_start()
{
    local PIDFILE=$RUN/$NAME.pid
    local START_OPTS=" \
        --emperor $ENABLED_CONFIGS_DIR \
        --pidfile $PIDFILE \
        --daemonize /var/log/$NAME/uwsgi-emperor.log"
    if do_pid_check $PIDFILE; then
        $NAME $DAEMON_OPTS $START_OPTS
    else
        echo "Already running!"
    fi
}
 
send_sig()
{
    local PIDFILE=$RUN/$NAME.pid
    set +e
    [[ -f $PIDFILE ]] && kill $1 $(cat $PIDFILE) > /dev/null 2>&1
    set -e
}
 
wait_and_clean_pidfile()
{
    local PIDFILE=$RUN/uwsgi.pid
    until do_pid_check $PIDFILE; do
        echo -n "";
    done
    rm -f $PIDFILE
}
 
do_stop()
{
    send_sig -3
    wait_and_clean_pidfile
}
 
do_reload()
{
    send_sig -1
}
 
do_force_reload()
{
    send_sig -15
}
 
get_status()
{
    send_sig -10
}
 
enable_configs()
{
    local configs
 
    if [[ $# -eq 0 || ${1,,} = 'all' ]]; then
        configs=$(diff $AVAILABLE_CONFIGS_DIR $ENABLED_CONFIGS_DIR \
            | grep $AVAILABLE_CONFIGS_DIR \
            | sed -re 's#.+: (.+)$#\1#')
    else
        configs=$@
    fi
 
    for c in $configs; do
        echo -n "Enabling $c..."
        [[ -f $ENABLED_CONFIGS_DIR/$c ]] && echo "Skipped" && continue
        [[ -f $AVAILABLE_CONFIGS_DIR/$c ]] && \
            ln -s $AVAILABLE_CONFIGS_DIR/$c $ENABLED_CONFIGS_DIR && \
            echo "Done" && \
            continue
        echo "Error"
    done
}
 
disable_configs()
{
    local configs
    if [[ $# -eq 0 || ${1,,} = 'all' ]]; then
        configs=$(find $ENABLED_CONFIGS_DIR -type l -exec basename {} \;)
    else
        configs=$@
    fi
 
    for c in $configs; do
        local config_path="$ENABLED_CONFIGS_DIR/$c"
        echo -n "Disabling $c..."
        [[ ! -L $config_path ]] && echo "Skipped" && continue
        [[ -f $config_path ]] && rm $config_path && echo "Done" && continue
        echo "Error"
    done
}
 
case "$OP" in
    start)
        echo "Starting $DESC: "
        do_start
        echo "$NAME."
        ;;
    stop)
        echo -n "Stopping $DESC: "
        do_stop
        echo "$NAME."
        ;;
    reload)
        echo -n "Reloading $DESC: "
        do_reload
        echo "$NAME."
        ;;
    force-reload)
        echo -n "Force-reloading $DESC: "
        do_force_reload
        echo "$NAME."
       ;;
    restart)
        echo  "Restarting $DESC: "
        do_stop
        sleep 1
        do_start
        echo "$NAME."
        ;;
    status)
        get_status
        ;;
    enable)
        shift
        enable_configs $@
        ;;
    disable)
        shift
        disable_configs $@
        ;;
    *)
        N=/etc/init.d/$NAME
        echo "Usage: $N {start|stop|restart|reload|force-reload|status|enable|disable}">&2
        exit 1
        ;;
esac
exit 0
```


chmod +x /etc/init.d/emperor
update-rc.d emperor defaults
