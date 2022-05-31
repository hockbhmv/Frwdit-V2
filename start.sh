echo "Cloning Repo...."
if [ -z $BRANCH ]
then
  echo "Cloning main branch...."
  git clone https://github.com/hockbhmv/Frwdit-V2 /Frwdit-V2 
else
  echo "Cloning $REPO_URL using $BRANCH branch...."
  git clone $REPO_URL -b $BRANCH /$DIR 
fi
cd /$DIR
pip3 install -U -r requirements.txt
echo "Starting Bot .... with $WORKER"
python3 $WORKER
