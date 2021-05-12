# -*- coding: utf-8 -*-

"""Module for dealing with transfers to the reMarkable

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2021, G.J.J. van den Burg

"""

import argparse
import sys

from rmapy.api import Client
from rmapy.document import ZipDocument
from rmapy.exceptions import ApiError, AuthError
from rmapy.folder import Folder

from .exceptions import RemarkableError
from .log import Logger


logger = Logger()


def authenticate_rmapy(token=None):
    msg = (
        "\n"
        "The reMarkable needs to be authenticated before we can upload.\n"
        "Please visit:\n\n"
        "\thttps://my.remarkable.com/connect/desktop\n"
        "\nand copy the one-time code for a desktop application.\n"
    )
    client = Client()
    if not client.is_auth():
        if token is None:
            print(msg)
            token = input("Please enter the one-time code: ")
            token = token.strip()
            print()
        try:
            client.register_device(token)
        except AuthError:
            raise RemarkableError(
                "Failed to authenticate the reMarkable client"
            )
    client.renew_token()
    if not client.is_auth():
        raise RemarkableError("Failed to authenticate the reMarkable client")
    return client


def upload_to_remarkable(filepath, remarkable_dir="/"):
    client = authenticate_rmapy()
    logger.info("Starting upload to reMarkable")

    is_folder = lambda x: isinstance(x, Folder)

    remarkable_dir = remarkable_dir.rstrip("/")
    if remarkable_dir:
        parts = remarkable_dir.split("/")
        parent_id = ""

        while parts:
            rmdir = parts.pop(0)
            if not rmdir:
                continue

            # get the folders with the desired parent
            folders = list(filter(is_folder, client.get_meta_items()))
            siblings = [f for f in folders if f.Parent == parent_id]

            # if the folder already exists, record its ID and continue
            match = next(
                (f for f in siblings if f.VissibleName == rmdir), None
            )
            if not match is None:
                parent_id = match.ID
                continue

            # create a new folder with the desired parent
            new_folder = Folder(rmdir)
            new_folder.Parent = parent_id

            try:
                client.create_folder(new_folder)
            except ApiError:
                raise RemarkableError(
                    f"Creating directory {remarkable_dir} on reMarkable failed"
                )
            parent_id = new_folder.ID

        # upload target is the folder with the last recorded parent_id
        target = next(
            filter(lambda i: is_folder(i) and i.ID == parent_id),
            client.get_meta_items(),
            None,
        )
        if target is None:
            raise RemarkableError(
                f"Creating directory {remarkable_dir} on reMarkable failed"
            )
    else:
        target = Folder(ID="")

    doc = ZipDocument(doc=filepath)
    try:
        client.upload(zip_doc=doc, to=target)
    except ApiError:
        raise RemarkableError(
            f"Uploading file {filepath} to reMarkable failed"
        )
    logger.info("Upload successful.")


def auth_cli():
    """Command line interface to authenticate rmapy"""
    parser = argparse.ArgumentParser("Authenticate the rmapy client")
    parser.add_argument("token", help="Authentication token", nargs="?")
    args = parser.parse_args()
    try:
        authenticate_rmapy(args.token)
    except RemarkableError:
        print("Authentication failed.", file=sys.stderr)
        raise SystemExit(1)
    print("Authentication successful.")
