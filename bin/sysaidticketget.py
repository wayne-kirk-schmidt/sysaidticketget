#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Explanation:

    This downloads SysAid tickets using a worker queue.
    Applicable for both Requests and Incidents this can be extended to other Service Requests.
    As this is also a work queue, processing can also be done post extraction.

Usage:
    $ python  sysaidticketget [ options ]

Style:
    Google Python Style Guide:
    http://google.github.io/styleguide/pyguide.html

    @name           sysaidticketget
    @version        1.0.0
    @author-name    Wayne Schmidt
    @author-email   wayne.kirk.schmidt@gmail.com
    @license-name   Apache
    @license-url    https://www.apache.org/licenses/LICENSE-2.0
"""

__version__ = '1.0.0'
__author__ = "Wayne Schmidt (wayne.kirk.schmidt@gmail.com)"

import argparse
import concurrent.futures
import datetime
import os
import queue
import re
import time
import tempfile
from pathlib import Path

import requests
import logging

logging.basicConfig(
    level=logging.ERROR,
    format="ERROR | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


"""
Accept 5 to 9 digits to address current use of 6 and past and future proof.
"""
TICKET_REGEX = re.compile(r"^\d{5,9}$")


"""
web action timeout
"""
HTTP_TIMEOUT_SECONDS = 30

"""
web status results we are tracking
"""
HTTP_STATUS_UNAUTHORIZED = 401
HTTP_STATUS_FORBIDDEN = 403
HTTP_STATUS_REDIRECT = 302

SYS_AID_TARGET = (
    "https://{tenant}.sysaidit.com/printhelpdesk.pdf?form=SREdit&page=0&id={ticket}"
)


def log_error(error_type, name, ticket, message):
    """
    Helper function for error messages, wrapping logger.error
    """
    logger.error(
        "[%s] ticket=%s type=%s error=%s",
        name,
        ticket,
        error_type,
        str(message),
    )

def parse_args():
    """
    Assemble Arguments. The goal is collect tenant, workers, sleep, and tickets.
    Once done, then we have the ability to submit the queue to the workers.
    """
    parser = argparse.ArgumentParser(
        description="Download SysAid ticket reports in PDF format"
    )
    parser.add_argument("--cookie", required=True, help="JSESSIONID value")
    parser.add_argument("--tenant", required=True, help="SysAid Tenant Value")
    parser.add_argument("--tickets", required=True, help="Ticket, comma list, or file path")
    parser.add_argument("--dst", default=None, help="Destination directory")
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--sleep", type=float, default=0.25)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def resolve_tickets(spec):
    """
    Determine the list of tickets to process. This can be a list or file.
    The contents are resolved into a list and used to populate the work queue.
    """
    path = Path(spec)

    if path.exists() and path.is_file():
        tickets = []
        for line in path.read_text().splitlines():
            line = line.strip()
            if line:
                tickets.append(line)
    elif "," in spec:
        tickets = [t.strip() for t in spec.split(",")]
    else:
        tickets = [spec.strip()]

    invalid = [t for t in tickets if not TICKET_REGEX.match(t)]
    if invalid:
        raise ValueError(f"Invalid ticket IDs: {invalid}")

    return tickets


def make_dst(dst):
    """
    Build a output directory to collect the results. Currently this is a PDF file.
    Future iterations could be a JSON file, or other formats. 
    The Output for the file will include the ticket number to avoid collisions.
    """
    if dst:
        base = Path(dst)
    else:
        today = datetime.date.today().strftime("%Y%m%d")

        base = Path(
            os.path.join(
                tempfile.gettempdir(),
                "tickets",
                today
            )
        )

    base = base.expanduser().resolve()
    base.mkdir(parents=True, exist_ok=True)
    return base


def ticket_output_path(dst: Path, ticket: str):
    """
    Return the final output path for a ticket PDF.
    """
    outfile = Path(
        os.path.join(
            dst,
            f"{ticket}-report.pdf"
        )
    )
    return outfile

def worker(name, input_queue, cookie, tenant, dst, sleep_s, verbose):
    """
    Define how the individual work in the pool does its work.
    Select a ticket, retrieve the content, write the output.
    """
    session = requests.Session()
    session.headers.update({
        "Cookie": f"JSESSIONID={cookie}"
    })

    while True:
        try:
            ticket = input_queue.get_nowait()
        except queue.Empty:
            return

        sysaid_url = SYS_AID_TARGET.format(
            tenant=tenant,
            ticket=ticket
        )

        outfile = ticket_output_path(dst, ticket)

        if verbose:
            print(f"[{name}] fetching {ticket}")

        try:
            response = session.get(sysaid_url, timeout=HTTP_TIMEOUT_SECONDS)
            response.raise_for_status()

            outfile.write_bytes(response.content)

            if verbose:
                print(f"[{name}] wrote {outfile}")

        except requests.exceptions.HTTPError as http_error:
            response = http_error.response
            status = response.status_code if response else None
            if status in (
               HTTP_STATUS_UNAUTHORIZED,
               HTTP_STATUS_FORBIDDEN,
               HTTP_STATUS_REDIRECT ):
                log_error("AUTH", name, ticket, http_error)
            else:
                log_error("HTTP", name, ticket, http_error)

        except requests.exceptions.Timeout:
            log_error("HTTP", name, ticket, "timeout")

        except requests.exceptions.RequestException as request_error:
            log_error("HTTP", name, ticket, request_error)

        except OSError as os_error:
            log_error("OUTPUT", name, ticket, os_error)

        except Exception as unknown_error:
            log_error("UNKNOWN", name, ticket, unknown_error)

        finally:
            input_queue.task_done()
            time.sleep(sleep_s)

def main():
    """
    Main driver of the script. 
    Build the ticket list, build the pool. Start the queue.
    """

    args = parse_args()

    tickets = resolve_tickets(args.tickets)
    dst = make_dst(args.dst)

    processing_queue = queue.Queue()
    for ticket in tickets:
        processing_queue.put(ticket)

    if args.verbose:
        print(f"Number Tickets : {len(tickets)}")
        print(f"Number Workers : {args.workers}")
        print(f"Destination    : {dst}")

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=args.workers
    ) as pool:
        for i in range(args.workers):
            pool.submit(
                worker,
                f"w{i + 1}",
                processing_queue,
                args.cookie,
                args.tenant,
                dst,
                args.sleep,
                args.verbose
            )

    ### processing_queue.join()


if __name__ == "__main__":
    main()
