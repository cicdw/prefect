#!/usr/bin/env python


import click
import json
import logging
import os
import requests
import sys
import prefect


@click.group()
def cli():
    """
    The Prefect CLI
    """
    pass


@cli.command()
@click.argument("storage_metadata")
@click.argument("environment_metadata")
def execute_flow(storage_metadata, environment_metadata):
    """"""
    storage_schema = prefect.serialization.storage.StorageSchema()
    storage = storage_schema.load(json.loads(storage_metadata))

    environment_schema = prefect.serialization.environment.EnvironmentSchema()
    environment = environment_schema.load(json.loads(environment_metadata))

    environment.setup(storage)
    environment.execute(storage)
