find . -iname '*.py' | xargs pylint --rcfile=pylintrc
rc=$(($rc+$?))

exit $rc
