#!/bin/bash

function step() {
  local tgt="step${1}"
  pushd .
  cd $tgt
  formchk -3 vibave.chk
  git add vibave.fchk
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
formchk -3 vibave.chk
git add vibave.fchk
popd
echo "done"

for m_dir in $(ls | grep mode); do
  echo "Working on mode ${m_dir}"
  mode $m_dir
  echo "Done"
done

echo "all done"
