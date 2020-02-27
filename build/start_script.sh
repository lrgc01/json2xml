#!/bin/bash

THIS="$0"

export SCRIPTDIR=${DOCK_SCRIPTDIR:-"/script"}
export WORKDIR=${DOCK_WORKDIR:-"/workdir"}
export RUNUSER=${DOCK_RUNUSER:-"pyuser"}
export USERHOME=${DOCK_USERHOME:-"/home/$RUNUSER"}
# Mandatory, otherwise quit program (Mode = A (transmitter) or B (receiver))
export SCRIPTMODE=${DOCK_SCRIPTMODE}

cd $WORKDIR

case ${SCRIPTMODE} in
	[aA]|[tT][rR][aA][nN][sS]*)
		SSHD="0"
		PY_SCRIPT="script_A.py"
		;;
	[bB]|[rR][eE][cC][vV]*)
		SSHD="1"
		PY_SCRIPT="script_B.py"
		;;
	*)
		exit 1
		;;
esac

if [ $(whoami)x = "rootx" ] ; then
   [ "${SSHD}" != "0" ] && /usr/sbin/sshd 
   env > environment.rc
   su $RUNUSER -s /bin/bash -c "sh $THIS $*"
   exit 0
fi

#set -x

#[ -f "./environment.rc" ] && . ./environment.rc
#export HOME=$USERHOME
#export WORKDIR=$BASEDIR

/usr/bin/python3 $SCRIPTDIR/$PY_SCRIPT
