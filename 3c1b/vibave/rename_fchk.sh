#!/bin/bash

function step() {
  local tgt="step${1}"
  pushd .
  cd $tgt
  git mv vibave.fchk rot.fchk
  popd
}

function mode() {
  pushd .
  cd $1
  step 1
  step 2
  popd
}

function exit_no_formcheck() {
  echo "no formchk set env properly"
  exit

}

which formchk || exit_no_formcheck

echo "doing ref_geom"
pushd .
cd refgeom
git mv vibave.fchk rot.fchk
popd
echo "done"

for m_dir in $(ls | grep mode); do
  echo "Working on mode ${m_dir}"
  mode $m_dir
  echo "Done"
done

echo "all done"
