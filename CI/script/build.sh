#! /bin/sh
if [ -z "${0}" -o -z "${1}" ]
then
    echo "command error"
	exit 1
fi
REALFILE=${0}
CUR_DIR=$(dirname ${REALFILE})
cd ${CUR_DIR}

cd ../..
baseDir=$(pwd)
nagiosdir=${baseDir}/${1}
echo ${nagiosdir}

srcdir_bin="${baseDir}/SRC/bin"
srcdir_etc="${baseDir}/SRC/etc"
srcdir_libexec="${baseDir}/SRC/libexec"
srcdir_setup="${baseDir}/SRC/setup.py"

if [ -d "${nagiosdir}" ]
then
   rm -rf "${nagiosdir}"
fi
mkdir "${nagiosdir}"
cp -r "${srcdir_bin}" "$nagiosdir"
cp -r "${srcdir_etc}" "$nagiosdir"
cp -r "${srcdir_libexec}" "$nagiosdir"
cp "${srcdir_setup}" "$nagiosdir"
if [ -d "${baseDir}/dist" ];then
   rm -rf "${baseDir}/dist"
fi
mkdir "${baseDir}/dist"
cd "${baseDir}"
tar cvf "${baseDir}/dist/${1}.tar" "${1}"
rm -rf "${nagiosdir}"