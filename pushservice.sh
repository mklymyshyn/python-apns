#!/bin/bash

# production one
CERT_PATH=$HOME/cert.pem

# sandbox or production mode
SANDBOX=0

SERVICE=`dirname $0`
PIDFILE=$SERVICE/apns.pid
LOGFILE=$SERVICE/logs/push.log
ENV=$HOME/env

BIN=$SERVICE/APNSWrapper/service.py

source $ENV/bin/activate

# go to service root
cd $SERVICE

case $1 in
start)
	echo "Starting APNS Service..."
	PYTHONPATH=.:.. python $BIN "$CERT_PATH" "$SANDBOX" &> $LOGFILE &
	PID_NUM=$!
	echo $PID_NUM > $PIDFILE
	echo "Done."
	;;
stop)
	echo "Stopping APNS Service..."
	kill `cat $PIDFILE`
	echo "Done."
	;;
restart)
	$0 stop
	$0 start
	;;
*)
	echo "Usage: $0 [start|stop|restart]"
	;;
esac

