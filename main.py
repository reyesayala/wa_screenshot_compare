import argparse
import csv
import sqlite3
import sys
import os
import requests
from bs4 import BeautifulSoup
import time
import asyncio
import urllib.request
import urllib.error
from pyppeteer import launch
from pyppeteer import errors
import logging
import signal
import re
from PIL import Image


from read_seed import *;
from create_archive_urls import *;
from screenshot import *;
from get_file_names import *;
from randomly_select_screenshots import *;
from calculate_similarity import *;
from crop_banners_from_images import *;


def init_func():
    print("*"*50);
    print("Hello, Welcom to Screenshot Compare!");
    print("Please select in the following option: ");
    print("-"*50);
    print("1: read_seed");
    print("2: create archive url");
    print("3: current screenshot");
    print("4: archive screenshot");
    print("5: get file names");
    print("6: randomly select screenshots");
    print("7: calculate similarity");
    print("8: similarity measures");
    print("9: crop banners");


    mode_val = input("Enter your mode number: ");
    return mode_val;

def read_seed():

    csv_in_name = input("Enter your input CSV: ");
    csv_out_name = "current_urls.csv";
    do_sort = False;
    extension = input("Enter archive ID: ");
    archive_name = input("Enter archive name: ");
    use_db = False;
    use_csv = True;

    print("Reading seed list...\n");
    parse_csv(csv_in_name, csv_out_name, do_sort, extension, use_db, use_csv);
    print("Process complete");

def create_archive_url():
    if not os.path.exists("current_urls.csv"):
        print("Missing Input file, Please Run Read Seed Mode (Mode 1)");
        exit();

    csv_out_name = "archive_urls.csv";
    csv_in_name = "current_urls.csv";
    remove_banner = True;

    print("Getting archive urls...")
    create_with_csv(csv_out_name, csv_in_name, remove_banner);
    print("Process complete")
    

def current_screenshot():
    if not os.path.exists("current_urls.csv"):
        print("Missing Input file, Please Run Read Seed (Mode 1)");
        exit();

    else: 
        csv_in_name = "current_urls.csv"
        csv_out_name = "current_index.csv"
        pics_out_path = "current_pics/"
        
        # TODO: if folder exist: clean folder option
        if not os.path.exists(pics_out_path):
            os.makedirs(pics_out_path)
        
        screenshot_method = 1
        timeout_duration = 30
        read_range = [0,1000]

        chrome_args = "--no-sandbox"
        chrome_args = re.sub(" +", " ", chrome_args)
        chrome_args = chrome_args.strip().split(" ")

        screensize = [768,1024]
        keep_cookies = False;
        mode = "current"

        signal.signal(signal.SIGINT, signal_handler_sigint)
        signal.signal(signal.SIGALRM, signal_handler_sigalrm)

        print("Taking screenshots")

        set_up_logging(pics_out_path, mode)

        print(screensize)
        screenshot_csv(csv_in_name, csv_out_name, pics_out_path, screenshot_method, timeout_duration, read_range,
                   chrome_args, screensize, keep_cookies, mode)
        
        print("The current screenshots have been created in this directory: ", pics_out_path)


def archive_screenshot():

    if not os.path.exists("archive_urls.csv"):
        print("Missing Input file, Please Run Create Archive (Mode 2)");
        exit();

    else: 
        csv_in_name = "archive_urls.csv"
        csv_out_name = "archive_index.csv"
        pics_out_path = "archive_pics/"
        
        # TODO: if folder exist: clean folder option
        if not os.path.exists(pics_out_path):
            os.makedirs(pics_out_path)
        
        screenshot_method = 1
        timeout_duration = 30
        read_range = [0,1000]

        chrome_args = "--no-sandbox"
        chrome_args = re.sub(" +", " ", chrome_args)
        chrome_args = chrome_args.strip().split(" ")

        screensize = [768,1024]
        keep_cookies = False;
        mode = "archive"

        signal.signal(signal.SIGINT, signal_handler_sigint)
        signal.signal(signal.SIGALRM, signal_handler_sigalrm)

        print("Taking screenshots")

        set_up_logging(pics_out_path, mode)

        print(screensize)
        screenshot_csv(csv_in_name, csv_out_name, pics_out_path, screenshot_method, timeout_duration, read_range,
                   chrome_args, screensize, keep_cookies, mode)
        
        print("The current screenshots have been created in this directory: ", pics_out_path)

def get_file_names():
    if not os.path.exists("current_index.csv"):
        print("Missing Input file, Please Run Create Archive (Mode 3)");
        exit();

    elif not os.path.exists("archive_index.csv"):
        print("Missing Input file, Please Run Create Archive (Mode 4)");
        exit();

    curr_csv_name = "current_index.csv"
    arch_csv_name = "archive_index.csv"
    do_print = True
    csv_out_name = "file_names.csv"
    open_with_csv(curr_csv_name, arch_csv_name, csv_out_name, do_print)

def randomly_select_screenshots():
    if not os.path.exists("file_names.csv"):
        print("Missing Input file, Please Run Create Archive (Mode 5)");
        exit();

    input_csv = "file_names.csv"
    out_file = "selected_file_names.csv"
    num = 5 
    total = 1000

    make_selection(input_csv, out_file, num, total)

def calculate_similarity():

    csv_in_name = "file_names.csv"
    curr_img_dir = "current_pics/"
    arch_img_dir = "archive_pics/"
    ssim_flag = True
    mse_flag = True
    vec_flag = True
    csv_out_name = "score.csv"
    do_print = True

    print("Reading the input files ...")
    image_dict, url_name_dict = read_input_file(csv_in_name, curr_img_dir, arch_img_dir)

    find_scores(image_dict, url_name_dict, ssim_flag, mse_flag, vec_flag, csv_out_name, do_print)
    

def similarity_measures():
    print("In process");
    print("8");

def crop_banners_from_images():
    input_dir = "archive_pics/"
    output_dir = "pics_archived_no_banners"
    new_dimensions = [0,43,1024,768]
    print("Reading the input files ...")
    crop_images(input_dir, output_dir, new_dimensions)


def mode_selector(mode):
    switcher = {
        1: read_seed,
        2: create_archive_url,
        3: current_screenshot,
        4: archive_screenshot,
        5: get_file_names,
        6: randomly_select_screenshots,
        7: calculate_similarity,
        8: similarity_measures,
        9: crop_banners_from_images
        
    }
    if (mode > 9 or mode <1):
        print("Invalid");
    else:
        switcher[mode]();


def main():

    mode = int(init_func());
    mode_selector(mode);

main();