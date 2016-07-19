#!/bin/sh
FILE="$$.tar.gz"
LIST="$$.list"
trap "rm -f ./tmp.sh $FILE $LIST" 0 1 2 3 9 11 15

NAME=`basename $0`
if [ "$NAME" == "release.sh" ];then
    cp -p release.sh ./tmp.sh
    exec ./tmp.sh
fi

git checkout master
git ls-files >$LIST
tar cfz $FILE `cat $LIST`

git checkout release
tar xvfz $FILE
git add `cat $LIST`

#git mvや git delが必要かも
#内容確認後 git commit

#そしたらgithubなどにpush
#git push origin
#git push -u github release:master

exit 0
