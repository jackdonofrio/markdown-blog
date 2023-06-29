# script to run the web server and set it up if necessary
# This assumes I'm only using one virtual env for this project (which I am for the foreseeable future)
if ! [[ -f "venv/bin/activate" ]] ; then
  echo "no virtual env detected ; now creating one and installing requisite packages"
  python3 -m venv venv
  source venv/bin/activate
  pip3 install -r requirements.txt

  # init database NOTE: (this part is for my debugging use, and may be removed)
  python3 -c 'from markdown_blog import db; db.create_all()'
fi
source venv/bin/activate
python3 run.py
