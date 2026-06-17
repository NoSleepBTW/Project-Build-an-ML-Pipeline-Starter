#!/usr/bin/env python
"""
Download the raw dataset from W&B and apply basic cleaning: drop price outliers,
parse review dates, and remove listings outside the NYC geographic area. The cleaned
result is uploaded back to W&B as a new artifact.
"""
import argparse
import logging
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()

def go(args):

    run = wandb.init(project="nyc_airbnb", group="cleaning", job_type="basic_cleaning", save_code=True)
    run.config.update(args)

    # Download the raw data artifact from W&B and load it
    logger.info("Downloading and reading artifact %s", args.input_artifact)
    artifact_local_path = run.use_artifact(args.input_artifact).file()
    df = pd.read_csv(artifact_local_path)
    rows_in = len(df)

    # Drop price outliers outside the configured [min_price, max_price] range
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()

    # Parse last_review into proper datetimes
    df['last_review'] = pd.to_datetime(df['last_review'])

    # Drop rows outside the NYC bounding box. This guards against the out-of-area
    # coordinates that appear in newer data samples (e.g. sample2.csv).
    idx = df['longitude'].between(-74.25, -73.50) & df['latitude'].between(40.5, 41.2)
    df = df[idx].copy()
    logger.info("Cleaning removed %d of %d rows", rows_in - len(df), rows_in)

    # Write the cleaned data and upload it to W&B as a new versioned artifact
    logger.info("Uploading cleaned artifact %s", args.output_artifact)
    df.to_csv('clean_sample.csv', index=False)

    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")
  
    parser.add_argument(
        "--input_artifact",
        type=str,
        help="Name of the input W&B artifact (raw data) to be cleaned, e.g. 'sample.csv:latest'",
        required=True
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="Name for the cleaned output W&B artifact, e.g. 'clean_sample.csv'",
        required=True
    )

    parser.add_argument(
        "--output_type",
        type=str,
        help="Type/category to assign to the output artifact in W&B",
        required=True
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help="A brief description of the output artifact",
        required=True
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help="Minimum price; listings below this value are dropped as outliers",
        required=True
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="Maximum price; listings above this value are dropped as outliers",
        required=True
    )


    args = parser.parse_args()

    go(args)
