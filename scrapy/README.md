# [Scrapy tutorial](https://docs.scrapy.org/en/latest/intro/tutorial.html)

## Start project
``` bash
fiete@ubu:~/Documents/studium/fuehrung_und_nachhaltigkeit/scrapy$ scrapy startproject csr_reports
fiete@ubu:~/Documents/studium/fuehrung_und_nachhaltigkeit/scrapy$ tree -L 1
.
├── csr_reports
└── README.md

1 directory, 1 file
```

### General project structure
``` bash
.
├── csr_reports                                 # project name
│   ├── csr_reports                             # project's Python module, you'll import your code from here
│   │   ├── __init__.py
│   │   ├── items.py                            # project items definition file
│   │   ├── middlewares.py                      # project middlewares file
│   │   ├── pipelines.py                        # project pipelines file
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-38.pyc
│   │   │   └── settings.cpython-38.pyc
│   │   ├── settings.py                         # project settings file
│   │   └── spiders                             # directory that contains all spiders
│   │       ├── example.py                      # individual spider (for example.com)
│   │       ├── __init__.py
│   │       └── __pycache__
│   │           └── __init__.cpython-38.pyc
│   └── scrapy.cfg
└── README.md
```

## Create spider
`scrapy genspider example example.com` creates a spider (`example.py`) in `csr_reports/spiders`.
``` bash
fiete@ubu:~/Documents/studium/fuehrung_und_nachhaltigkeit/scrapy/csr_reports$ scrapy genspider example example.com
fiete@ubu:~/Documents/studium/fuehrung_und_nachhaltigkeit/scrapy/csr_reports$ tree -L 3
.
├── csr_reports
│   ├── ...
│   ├── ...
│   │   ├── ...
│   │   └── ...
│   ├── ...
│   └── spiders
│       ├── example.py
│       ├── ...
│       └── ...
└── scrapy.cfg

4 directories, 10 files
```

## Run the spider
`scrapy crawl example`