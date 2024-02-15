import functools
import inspect
import logging
from typing import Callable, Any, List, Optional

from .proxmox import get_proxmox_api, resolve_vm_identifier
from .session_config import SessionConfig

def command(description: Optional[str] = None) -> Callable:
    def decorator(func: Callable) -> Callable:
        func.__description__ = description if description is not None else "No description available."
        func_name_parts = func.__name__.split('_', 1)
        func.__group__ = func_name_parts[0] if len(func_name_parts) > 1 else 'default'
        func.__command__ = func_name_parts[-1]
        func.__params__ = inspect.signature(func).parameters

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> str:
            try:
                prepared_args = _prepare_function_call(func, *args, **kwargs)
                return _execute_proxmox_command(func, *prepared_args)
            except Exception as e:
                logging.debug(f"Error executing command {func.__name__}: {e}")
                return str(e)

        return wrapper

    return decorator

def _prepare_function_call(func: Callable, *args: Any, **kwargs: Any) -> List[Any]:
    call_args = [get_proxmox_api()]
    session_node = SessionConfig.get_node()

    if 'node_name' in func.__params__ and 'node_name' not in kwargs:
        if session_node:
            call_args.append(session_node)
        elif args:
            call_args.append(args[0])
            args = args[1:]

    if 'vm_id' in func.__params__:
        node_name = call_args[1] if len(call_args) > 1 else None
        vm_id = args[0] if args else kwargs.get('vm_id')
        if vm_id is not None:
            resolved_vm_id = resolve_vm_identifier(node_name, vm_id)
            if resolved_vm_id is None:
                raise ValueError(f"🔴 Could not resolve VM identifier: {vm_id}")
            if 'vm_id' in kwargs:
                kwargs['vm_id'] = resolved_vm_id
            else:
                args = (resolved_vm_id,) + args[1:]

    try:
        bound_args = inspect.signature(func).bind(*call_args, *args, **kwargs)
        bound_args.apply_defaults()
    except TypeError as e:
        raise TypeError(f"🔴 TypeError in {func.__name__}: {e}.")

    return list(bound_args.args)

def _execute_proxmox_command(func: Callable, *args: Any) -> str:
    if args[0] is None:
        return "🔴 Failed to connect to Proxmox API."
    try:
        return func(*args)
    except TypeError as e:
        return f"🔴 TypeError in {func.__name__}: {e}"
    except ValueError as e:
        return f"🔴 Could not resolve VM identifier: {e}"
    except Exception as e:
        return f"🔴 Error processing your request in {func.__name__}: {e}"
