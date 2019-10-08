rm ognddbfuncs.py kglid.py 
cp /nfs/OGN/src/funcs/ognddbfuncs.py .
cp /nfs/OGN/src/kglid.py .
git add .
git commit
git push origin master
git push glidernet master
