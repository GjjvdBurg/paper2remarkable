# -*- coding: utf-8 -*-

"""Module for dealing with transfers to the reMarkable

Author: G.J.J. van den Burg
License: See LICENSE file
Copyright: 2021, G.J.J. van den Burg


"""

import subprocess

from .exceptions import RemarkableError
from .log import Logger


logger = Logger()


def upload_to_remarkable_rmapi(
    filepath, remarkable_dir="/", rmapi_path="rmapi"
):
    logger.info("Starting upload to reMarkable using rMapi")

    # Create the reMarkable dir if it doesn't exist
    remarkable_dir = remarkable_dir.rstrip("/")
    if remarkable_dir:
        parts = remarkable_dir.split("/")
        rmdir = ""
        while parts:
            rmdir += "/" + parts.pop(0)
            status = subprocess.call(
                [rmapi_path, "mkdir", rmdir],
                stdout=subprocess.DEVNULL,
            )
            if not status == 0:
                raise RemarkableError(
                    "Creating directory %s on reMarkable failed"
                    % remarkable_dir
                )

    # Upload the file
    status = subprocess.call(
        [rmapi_path, "put", filepath, remarkable_dir + "/"],
        stdout=subprocess.DEVNULL,
    )
    if not status == 0:
        raise RemarkableError(
            "Uploading file %s to reMarkable failed" % filepath
        )
    logger.info("Upload successful.")


def upload_to_remarkable_rmapy(filepath, remarkable_dir="/"):
    from rmapy.api import Client
    from rmapy.document import ZipDocument
    from rmapy.folder import Folder
    from rmapy.exceptions import ApiError, AuthError

    client = Client()
    if not client.is_auth():
        print(
            "\nThe reMarkable needs to be authenticated before we can upload."
        )
        print("Please visit:\n")
        print("\thttps://my.remarkable.com/connect/desktop")
        print("\nand copy the one-time code for a desktop application.\n")
        code = input("Please enter the one-time code: ")
        code = code.strip()
        print()
        try:
            client.register_device(code)
        except AuthError:
            raise RemarkableError(
                "Failed to authenticate the reMarkable client"
            )

    client.renew_token()
    if not client.is_auth():
        raise RemarkableError("Failed to authenticate the reMarkable client")

    logger.info("Starting upload to reMarkable using rmapy")

    remarkable_dir = remarkable_dir.rstrip("/")
    if remarkable_dir:
        parts = remarkable_dir.split("/")
        parent_id = ""

        while parts:
            rmdir = parts.pop(0)
            if not rmdir:
                continue

            # get the folders with the desired parent
            folders = [
                i for i in client.get_meta_items() if isinstance(i, Folder)
            ]
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
                    "Creating directory %s on reMarkable failed"
                    % remarkable_dir
                )
            parent_id = new_folder.ID

        # upload target is the folder with the last recorded parent_id
        target = next(
            (
                i
                for i in client.get_meta_items()
                if isinstance(i, Folder) and i.ID == parent_id
            ),
            None,
        )
        if target is None:
            raise RemarkableError(
                "Creating directory %s on reMarkable failed" % remarkable_dir
            )
    else:
        target = Folder(ID="")

    doc = ZipDocument(doc=filepath)
    try:
        client.upload(zip_doc=doc, to=target)
    except ApiError:
        raise RemarkableError(
            "Uploading file %s to reMarkable failed" % filepath
        )
    logger.info("Upload successful.")


def get_remarkable_backend(rmapi_path="rmapi"):
    try:
        status = subprocess.call(
            [rmapi_path, "version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        pass

    if status == 0:
        return "rmapi"

    try:
        import rmapy

        assert rmapy

        return "rmapy"
    except ImportError:
        pass

    return None


def upload_to_remarkable(filepath, remarkable_dir="/", rmapi_path="rmapi"):
    backend = get_remarkable_backend(rmapi_path=rmapi_path)
    if backend is None:
        raise RemarkableError("Couldn't find a suitable reMarkable client.")
    if backend == "rmapi":
        upload_to_remarkable_rmapi(
            filepath, remarkable_dir=remarkable_dir, rmapi_path=rmapi_path
        )
    elif backend == "rmapy":
        upload_to_remarkable_rmapy(filepath, remarkable_dir=remarkable_dir)
    else:
        raise RemarkableError("Unknown reMarkable client: %s" % backend)
