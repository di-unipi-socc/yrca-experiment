cp all.json yRCA/all.log
cp template.yml yRCA/template.yml
cp explain.json yRCA/error.json

cd yRCA/

python3 yrca.py error.json all.log template.yml
