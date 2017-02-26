#!/bin/bash

LINT_COMMAND="--pylint --pylint-error-types=WEF"
DOCTEST_COMMAND="--doctest-modules"
COVERAGE_COMMAND="--cov=smserver"

if [ "$NO_LINT" = "1" ] ; then
    LINT_COMMAND="";
fi;

if [ "$NO_DOCTEST" = "1" ] ; then
    DOCTEST_COMMAND="";
fi;

if [ "$NO_COVERAGE" = "1" ] ; then
    COVERAGE_COMMAND="";
fi;

pytest $LINT_COMMAND $DOCTEST_COMMAND $COVERAGE_COMMAND --old-summary smserver test
