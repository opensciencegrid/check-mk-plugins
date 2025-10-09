#!/bin/bash
STATE_OK=0
STATE_WARNING=1
STATE_CRITICAL=2
STATE_UNKNOWN=3
msg=""
current_month=$(date -d "today" +"%Y.%m")
while read c
do
        if [[ "$c" =~ "." || "$c" =~ ^"route-views" ]]
        then
                d="${c}"
        else
                d="route-views.${c}"
        fi


        path_r=https://kennesaw-origin.nationalresearchplatform.org:8443/routeviews/$d/bgpdata/$current_month
        http_code=$(curl --write-out "%{http_code}" --silent --output /dev/null "$path_r")

        if  [[ $http_code != "200" ]]
        then
                 msg="$msg /routeviews/routeviews/$d/bgpdata/$current_month not found; "
        fi
done < ~/local/lib/nagios/plugins/incremental-dirs-routeview.txt

if [[ -z "$msg" ]]; then
        exit $STATE_OK
    else
        echo $msg
        exit $STATE_CRITICAL
    fi
