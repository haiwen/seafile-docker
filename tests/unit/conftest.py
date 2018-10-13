import os
import sys
from os.path import abspath, basename, exists, dirname, join

import pytest

project_dir = join(dirname(abspath(__file__)), '../..')
scripts_dir = join(project_dir, 'scrpits')
