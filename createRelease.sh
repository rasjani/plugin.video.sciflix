#!/bin/sh
# TODO: Add version from latest git tag
VERSION=0.4
ROOT=`pwd`
PLUGINNAME="plugin.video.sciflix"

rm -rf ./releases/tmp/
mkdir ./releases/${VERSION}
mkdir -p ./releases/tmp/${PLUGINNAME}/resources/language/English
mkdir -p ./releases/tmp/${PLUGINNAME}/resources/language/Finnish
mkdir -p ./releases/tmp/${PLUGINNAME}/resources/lib

cp ./icon.png ./releases/tmp/${PLUGINNAME}
cp ./addon.py ./releases/tmp/${PLUGINNAME}
cp ./addon.xml ./releases/tmp/${PLUGINNAME}
cp ./changelog.txt ./releases/tmp/${PLUGINNAME}
#cp ./fanart.png ./releases/tmp/${PLUGINNAME}
#cp ./icon.png ./releases/tmp/${PLUGINNAME}
cp ./LICENSE.txt ./releases/tmp/${PLUGINNAME}
cp ./README.md ./releases/tmp/${PLUGINNAME}
cp ./resources/__init__.py ./releases/tmp/${PLUGINNAME}/resources/
cp ./resources/language/English/strings.xml ./releases/tmp/${PLUGINNAME}/resources/language/English
cp ./resources/language/Finnish/strings.xml ./releases/tmp/${PLUGINNAME}/resources/language/Finnish
cp ./resources/lib/__init__.py ./releases/tmp/${PLUGINNAME}/resources/lib
cd releases/tmp/
cp ${ROOT}/changelog.txt ../${VERSION}/changelog-${VERSION}.txt
## http://wiki.xbmc.org/index.php?title=Add-on_repositories is not very clear
## of image formats so in future, this might be changed .. 
if [ -f ${ROOT}/fanart.png  ]; then
  echo cp ${ROOT}/fanart.png ../${VERSION}/
fi
if [ -f ${ROOT}/icon.png  ]; then
  echo cp ${ROOT}/icon.png ../${VERSION}/
fi
zip -r ../${VERSION}/plugin.video.sciflix-${VERSION}.zip plugin.video.sciflix/*
