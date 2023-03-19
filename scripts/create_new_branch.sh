#!/bin/sh
# bash script to create a new branch that respects the library standard
#### bash scripts/create_new_branch.sh "[FEAT] - Implement instrument types #14"
#### bash scripts/create_new_branch.sh "[FEAT] Implement instrument types #14"
#### bash scripts/create_new_branch.sh "[FEAT] - Implement instrument types#14"
base_issue=$1
issue_number=${base_issue##*#}
issue="${base_issue%%#*}"
issue="${issue//\[FEAT\] \- /}"
issue="${issue/\[FEAT\] /}"
issue="${issue/\[FEAT\]/}"
issue="${issue// /\_}"
if [[ ${base_issue,} =~ "fix" ]]; then
  branch_name="fix/issue-$issue_number ${issue,,}"
else
  branch_name="feat/issue-$issue_number ${issue,,}"
fi
branch_name="${branch_name// /\_}"
last_char="${branch_name: -1}"
if [ "$last_char" = "_" ]
then
  branch_name=${branch_name::-1}
fi
git checkout -b $branch_name