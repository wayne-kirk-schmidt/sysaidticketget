#!/usr/bin/env bash

umask 022
export PATH="/usr/local/bin:/usr/local/sbin:/usr/bin:/usr/sbin:/bin:/sbin:$PATH"

sysaidtenant="${1}"
sysaidcookie="${2}"
sysaidticket=${3}
sleeptime="${4:-.25}"

sysaidtarget="https://${sysaidtenant}.sysaidit.com/printhelpdesk.pdf?form=SREdit&page=0&id=${sysaidticket}"
echo $sysaidtarget

outputbase="/tmp"
outputdir="${outputbase}/output-$( date +%Y%m%d )"
mkdir -p "${outputdir}"

outputfile="${outputdir}/${sysaidticket}-report.pdf"
rm -f "${outputfile}"

curl \
    -H "Cookie: JSESSIONID=${sysaidcookie}" \
    -L "${sysaidtarget}" \
    -o "${outputfile}"

sleep "${sleeptime}"
