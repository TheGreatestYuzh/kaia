from typing import *
from uuid import uuid4
from dataclasses import dataclass, field
from pathlib import Path
from abc import ABC, abstractmethod
from dataclasses import dataclass
from copy import copy
from .arguments_validator import ArgumentsValidator


T = TypeVar('T')


def fix_decider_and_decider_method(decider:  Union[str,type,Callable], decider_method: Union[None, str, Callable]) \
        -> tuple[str,str, Callable]:

    _method_to_validate = None
    fixed_decider_method = None

    if isinstance(decider, type):
        fixed_decider = decider.__name__
    elif isinstance(decider, str):
        fixed_decider = decider
    elif callable(decider):
        if decider_method is not None:
            raise ValueError("decider is callable, but decider_method is not None. Callable decider sets both decider and decider_method")
        _method_to_validate = decider
        parts = decider.__qualname__.split('.')
        if len(parts) > 2:
            raise ValueError("If `decider` is a function, it must be exactly 2 parts in qualname, Type.Method")
        fixed_decider = parts[0]
        fixed_decider_method = parts[1]
    else:
        raise ValueError(f'decider must be str, type, or callable type method, but was {decider}')

    if callable(decider_method):
        fixed_decider_method = decider_method.__name__
        _method_to_validate = decider_method
    elif isinstance(decider_method, str):
        fixed_decider_method = decider_method
    elif decider_method is None:
        pass
    else:
        raise ValueError(f'decider must be str, method or None, but was {decider}')

    return fixed_decider, fixed_decider_method, _method_to_validate


def fix_arguments_and_dependencies(arguments, dependencies, fake_dependencies: Optional[List[Union[str,'BrainBoxTask']]]) -> tuple[dict, dict]:
    if arguments is None:
        arguments = {}
    if dependencies is None:
        dependencies = {}

    for key in arguments:
        if key in dependencies:
            raise ValueError("Key {key} exist in both arguments and dependencies")

    fixed_dependencies = {}
    for key, value in dependencies.items():
        if isinstance(value, BrainBoxTask):
            fixed_dependencies[key] = value.id
        elif isinstance(value, str):
            fixed_dependencies[key] = value
        else:
            raise ValueError(f"Dependencies should be str or BrainBoxTask, but at key {key} was {value}")

    fixed_arguments = {}
    for key, value in arguments.items():
        if isinstance(value, BrainBoxTask):
            fixed_dependencies[key] = value.id
        else:
            fixed_arguments[key] = value

    if fake_dependencies is not None:
        for index, fake_dependency in enumerate(fake_dependencies):
            if isinstance(fake_dependency, BrainBoxTask):
                fake_dependency = fake_dependency.id
            elif isinstance(fake_dependency, str):
                pass
            else:
                raise ValueError(f"Fake Dependency should be list of str or BrainBoxTask, but element #{index} was {fake_dependency}")
            fixed_dependencies['*fake_dependency_'+str(index)] = fake_dependency

    return fixed_arguments, fixed_dependencies


def check_method(method_to_validate, arguments, dependencies):
    validator = ArgumentsValidator.from_signature(method_to_validate)
    array = []
    array.extend(arguments)
    array.extend(dependencies)
    validator.validate(array)



class BrainBoxTask:
    def __init__(self,
                 *,
                 decider: Union[str,type,Callable],
                 arguments: Optional[Dict[str,Any]] = None,
                 id: str | None = None,
                 dependencies: Optional[Dict[str,Union[str, 'BrainBoxTask']]] = None,
                 fake_dependencies: Optional[List[Union[str,'BrainBoxTask']]] = None,
                 info: Any = None,
                 batch: str|None = None,
                 decider_method: Union[None, str, Callable] = None,
                 decider_parameters: None|str = None,
                 ordering_token: str|None = None,
                 ):
        if id is not None:
            self.id = id
        else:
            self.id = BrainBoxTask.safe_id()

        self.decider, self.decider_method, _method_to_validate = fix_decider_and_decider_method(decider, decider_method)

        self.arguments, self.dependencies = fix_arguments_and_dependencies(arguments, dependencies, fake_dependencies)
        if _method_to_validate is not None:
            check_method(_method_to_validate, self.arguments, self.dependencies)

        self.info = info
        self.batch = batch
        self.decider_parameters = decider_parameters
        self.ordering_token = ordering_token


    def __repr__(self):
        return self.__dict__.__repr__()

    @staticmethod
    def call(type: Type[T]) -> T:
        from .task_builder import BrainBoxTaskBuilder
        return BrainBoxTaskBuilder(type)

    @staticmethod
    def safe_id():
        return 'id_'+str(uuid4()).replace('-','')


    def clone(self, **kwargs):
        result = copy(self)
        for k, v in kwargs.items():
            setattr(result, k, v)
        return result


