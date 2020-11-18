# pogometrics

## Required

- Python 3.8 +,  virtualenv
- Packages from `requirements.txt`
- Bbox for queries limiting ( use http://bboxfinder.com )
- Database and initial tables from `migrations/0.sql`

## Getting Started

1. Clone `git clone https://github.com/lenisko/pogometrics && cd pogometrics` repository and enter directory
2. Copy config template `cp config.example.yml config.yml`
3. Make changes in `config.yml`
4. Create python3 virtualenv `virtualenv -p python3 env`
5. Activate virtual env `source env/bin/activate`
6. Run `pip3 install -r requirements.txt`
7. Execute `./env/bin/python main.py` to run script

## TODO

* Better errors handling
* Take over the world
* More metrics

## LICENSE

            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                    Version 2, December 2004

 Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>

 Everyone is permitted to copy and distribute verbatim or modified
 copies of this license document, and changing it is allowed as long
 as the name is changed.

            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

  0. You just DO WHAT THE FUCK YOU WANT TO.