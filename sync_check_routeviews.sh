#!/bin/bash

current_month=$(date -d "today" +"%Y.%m")
while read c
do
        if [[ "$c" =~ "." || "$c" =~ ^"route-views" ]]
        then
                d="${c}"
        else
                d="route-views.${c}"
        fi


        path_r=https://kennesaw-origin.nationalresearchplatform.org:8443/routeviews/routeviews/$d/bgpdata/$current_month
        http_code=$(curl --write-out "%{http_code}" --silent --output /dev/null "$path_r")

        if  [[ $http_code != "200" ]]
        then
                 echo $path_r " not found"
        fi
done < incremental-dirs-routeview.txt
