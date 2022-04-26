echo "Cloning Repo...."
if [ -z $BRANCH ]
then
  echo "Cloning main branch...."
  git clone https://github.com/hockbhmv/Frwdit-V2 /Frwdit-V2 
else
  echo "Cloning $BRANCH branch...."
  git clone https://github.com/hockbhmv/Frwdit-V2 -b $BRANCH /Frwdit-V2 
fi
cd /Frwdit-V2 
pip3 install -U -r requirements.txt
echo "Starting Bot...."
python3 main.py
