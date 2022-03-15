import boto3
import json
import os
import requests
import argparse

from os import environ as env

from time import sleep

AWS_ACCESS_KEY_ID = env.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env.get("AWS_SECRET_ACCESS_KEY")
AWS_REGION = env.get("AWS_REGION")
s3 = boto3.client("s3",
        aws_access_key_id = AWS_ACCESS_KEY_ID,
        aws_secret_access_key = AWS_SECRET_ACCESS_KEY,
        region_name = AWS_REGION)

APPLICATION_ID = env.get("APPLICATION_ID")
TEST_SERVERS = env.get("TEST_SERVERS")

BOT_TOKEN = env.get("BOT_TOKEN")
HEADERS = {"Authorization": f"Bot {BOT_TOKEN}"}

BUCKET = env.get("AWS_BUCKET")
KEY = "commands.json"

global_url = f"https://discord.com/api/v8/applications/{APPLICATION_ID}/commands"
guild_urls = [f"https://discord.com/api/v8/applications/{APPLICATION_ID}/guilds/{test_server_id}/commands" for test_server_id in TEST_SERVERS]

def get_json(bucket, key):
    result = s3.get_object(Bucket=bucket, Key=key)
    try:
        text = result["Body"].read().decode()
    except Exception as e:
        print(f"Err: No file found at {bucket}/{key}: {e}")
    return json.loads(text)

def publish_command(url, commands):
    r = requests.post(url, headers = HEADERS, json = commands)
    if r.status_code != 200:
        sleep(20)
        print(f"Post to {url} failed; retrying once")
        r = requests.post(url, headers = HEADERS, json = commands)

    print(f"Response from {url}: {r.text}")

def get_all_commands(url):
    existing_commands = requests.get(url, headers = HEADERS).json()
    if not existing_commands:
        return []

def delete_command(url):
    r = requests.delete(url, headers = HEADERS)
    print(r.text)

def run_test():
    commands = get_json(BUCKET, KEY)
    for url in guild_urls:
        for command in commands:
            publish_command(url, command)

def run_global():
    commands = get_json(BUCKET, KEY)
    for command in commands:
        publish_command(global_url, command)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--test", dest = "test", action="store_const", const = True, default = False)

    args = parser.parse_args()
    if args.test:
        run_test();
    else:
        run_global()
