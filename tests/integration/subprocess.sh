#!/bin/bash

# Expected input from stdin:
# streamNo delay message
# Running the following
#
# (cat <<EOF
# 2 1 one\\\\n
# 1 2 two\\\\n
# 1 5 four
# 1 6 \\\\rNo, three..\\\\n
# EOF
# ) | ./subprocess.sh
#
# Would result in:
# one (after a delay of 1 sec. on stderr)
# two (after a delay of another second on stdout)
# four (after a delay of three more seconds on stdout)
# No, three.. (overwrites the line with "four" after a second)

while read line; do
	[[ -z $line ]] && continue
	stream=${line%% *}
	rest=${line#* *}
	delay=${rest%% *}
	message=${rest#* }
	eval "sleep $delay; printf \"$message\" >&$stream" &
done
wait
