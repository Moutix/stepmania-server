#! /bin/sh

echo "---------------- DOCTEST --------------------"
py.test --doctest-modules smserver


echo "---------------- UNIT TEST --------------------"
py.test test
