#!/bin/bash

echo "# NEMD_CO2" >> README.md
git init
git add *
git commit -m "first commit"
git remote add origin https://github.com/Darz2/NEMD_CO2.git
git push -u origin master