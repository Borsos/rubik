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

import traceback

class Storage(object):
    def __init__(self, factory):
        self._factory = factory
        def f_closure(self_, name):
            def f(x):
                try:
                    v = self_.add(x)
                except:
                    traceback.print_exc()
                    raise
                return self_
            for a in 'func_name', '__name__':
                setattr(f, a, name)
            return f
        self._store = f_closure(self, self._factory.__name__)
#        def f_closure_const(self_, name, const):
#            def f():
#                try:
#                    v = self_.add(const)
#                except:
#                    traceback.print_exc()
#                    raise
#                return v
#            for a in 'func_name', '__name__':
#                setattr(f, a, name)
#            return f
#        self._store = f_closure(self, self._factory.__name__)

    @property
    def store(self):
        return self._store

#    def store_const(self, const):
#        store_const_closure = f_closure(self, self._factory.__name__, const)
#        return store_const_closure

    def factory(self, value):
        return self._factory(value)

    def add(self, value):
        raise NotImplementedError("{0}.add".format(self.__class__.__name__))
   
        self._store_const = f_closure(self, self._factory.__name__)

    @property
    def store(self):
        return self._store

    def store_const(self, const):
        lambda : self.store(const)

    def factory(self, value):
        return self._factory(value)

    def add(self, value):
        raise NotImplementedError("{0}.add".format(self.__class__.__name__))
   
