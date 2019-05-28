mv ognddbdata.csv ognddbdata.csv.bkup
mv ognddbdata.txt ognddbdata.txt.bkup
wget ddb.glidernet.org/download -O ognddbdata.csv
python ognbuilfile.py
