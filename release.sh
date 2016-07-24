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
git ls-files |egrep -v "(test|example)"/ >$LIST
tar cfz $FILE `cat $LIST`

git checkout release
tar xvfz $FILE
git add `cat $LIST`

#git mvや git delが必要かも
#内容確認後 git commit
#まだ、test/ exmaple/はgithubに未公開

#そしたらtagつけてgithubなどにpush
#git tag V1.0
#git push origin
#git push origin V1.0
#git push -u github release:master   #-u済みでも明示しないとreleaseブランチ行く
#git push github V1.0

exit 0
