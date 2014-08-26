#!/usr/bin/env python3
#
# Copyright 2014 Simone Campagna
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

__author__ = "Simone Campagna"

__all__ = [
           'output_mode_callback',
           'get_output_mode_callback',
           'set_output_mode_callback',
          ]

OUTPUT_MODE_CALLBACK = None

def set_output_mode_callback(callback):
    global OUTPUT_MODE_CALLBACK
    OUTPUT_MODE_CALLBACK = callback

def get_output_mode_callback():
    global OUTPUT_MODE_CALLBACK
    return OUTPUT_MODE_CALLBACK
    
def output_mode_callback():
    global OUTPUT_MODE_CALLBACK
    if OUTPUT_MODE_CALLBACK is not None:
        OUTPUT_MODE_CALLBACK()
