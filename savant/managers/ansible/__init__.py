import logging
import os
import importlib

import yaml

from . import primitives
from .role_dirs import defaults_dir, files_dir, handlers_dir, meta_dir, tasks_dir, templates_dir, vars_dir

class Role(object):
    '''This object encapsulates all knowledge about how to build Ansible
    playbooks. Roles are structured according to Ansible best practices. See:

    http://docs.ansible.com/ansible/playbooks_best_practices.html'''

    top_dirs = ['tasks', 'handlers', 'templates', 'files', 'vars', 'defaults',
            'meta']

    def __init__(self, path, facts):
        self.path = path
        self.facts = facts
        self.logger = logging.getLogger(__name__ + '.' + type(self).__name__)

        assert os.path.isdir(self.path)

        self.directory_handlers = {}
        for dir_name in Role.top_dirs:
            self.set_dir_handlers(dir_name)

    def set_dir_handlers(self, dir_name):
        '''Dynamically load directory name as an object of the correct
        class.'''
        # tasks => tasks_dir
        path_name = dir_name+'_dir'
        module_name = globals()[path_name]
        # tasks => Tasks
        class_name = dir_name.capitalize()
        # == tasks_dir.Tasks
        DirModule = getattr(module_name, class_name)

        self.directory_handlers[dir_name] = DirModule(self.path)

    def translate_set(self, set_obj):
        PrimitiveClass = primitives.get_class(set_obj.info.system)
        primitive = PrimitiveClass(set_obj, self.facts)
        primitive.update_directives(self.directory_handlers)
