#coding: UTF-8

import os
import shutil
from os.path import abspath, basename, dirname, exists, join

from android.utils import read_file_content

KEYS_DIR = join(dirname(abspath(__file__)), '../../keys')

def get_keyfile(fn):
    return join(KEYS_DIR, fn)

def copy_keys(keyfile, targetdir):
    src = join(KEYS_DIR, keyfile)
    dst = join(targetdir, keyfile)
    assert exists(src), src
    if exists(dst):
        os.unlink(dst)
    shutil.copy(src, dst)

def read_key_file(keyfile):
    return read_file_content(get_keyfile(keyfile))
