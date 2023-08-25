while read p; do                                                                           
                   
        ip=`host $p | grep 'has address'| awk {'print $4'}`
        echo "$p $ip"
done < "hosts"





mkdir osg
cd osg
git clone https://github.com/cvmfs-contrib/config-repo.git -b osg

cd ..

mkdir egi
cd egi
git clone https://github.com/cvmfs-contrib/config-repo.git -b egi

cd ..

mkdir master
cd master
git clone https://github.com/cvmfs-contrib/config-repo.git -b master

cd ..

mkdir default
cd default
git clone https://github.com/cvmfs-contrib/config-repo.git -b default

cd ..

while read p; do                                                                           

  echo $p
  ip=`host $p | grep 'has address'| awk {'print $4'}`
  echo "$p $ip"

  echo "OSG"
  grep -R $p osg | wc -l 

  echo "EGI"
  grep -R $p egi | wc -l 

  echo "MASTER"
  grep -R $p master | wc -l 

  echo "default"
  grep -R $p default | wc -l 
  
done < "hosts"




# curl -u "838862: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" \
  "https://geolite.info/geoip/v2.1/country/$ip?pretty"
