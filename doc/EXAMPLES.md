# Examples

```bash
./bin/getsysaidpdf.ksh TENANT JSESSIONID 456789
```

```bash
python python/getsysaid-tickets.py --tenant TENANT --cookie JSESSIONID --tickets examples/tickets.txt
python python/getsysaid-tickets.py --tenant TENANT --cookie JSESSIONID --tickets 456789
```

```bash
usage: sysaidticketget.py [-h] --cookie COOKIE --tenant TENANT --tickets TICKETS [--dst DST] [--workers WORKERS] [--sleep SLEEP] [--verbose]

Download SysAid ticket reports in PDF format

options:
  -h, --help         show this help message and exit
  --cookie COOKIE    JSESSIONID value
  --tenant TENANT    SysAid Tenant Value
  --tickets TICKETS  Ticket, comma list, or file path
  --dst DST          Destination directory
  --workers WORKERS
  --sleep SLEEP
  --verbose
```
