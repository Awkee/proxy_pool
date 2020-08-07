#!/usr/bin/env bash

start_web()
{
	nohup python proxyPool.py webserver >/dev/null 2>&1 &
}

start_cron()
{
	nohup python proxyPool.py schedule >/dev/null 2>&1 &
}

usage()
{
cat <<END
usage:
	`basename $0` <web|cron>
END
}

case "$1" in
	web)
		start_web
		;;
	cron)
		start_cron
		;;
	*)
		usage
		;;
esac
