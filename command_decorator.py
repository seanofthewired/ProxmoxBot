import functools
import inspect
import logging
from proxmox import get_proxmox_api, resolve_vm_identifier
from session_config import SessionConfig

logging.basicConfig(level=logging.INFO)

def command(description: str, requires_vm_id=True, requires_node_name=False):
    def decorator(func):
        func.__description__ = description
        func_name_parts = func.__name__.split('_', 1)
        func.__group__ = func_name_parts[0] if len(func_name_parts) > 1 and func_name_parts[0] != 'default' else ''
        func.__command__ = func_name_parts[-1]
        func.__params__ = list(inspect.signature(func).parameters.keys())[1:]  # Exclude 'self' parameter

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            proxmox = get_proxmox_api()
            if proxmox is None:
                logging.error("Failed to connect to Proxmox API.")
                return "Failed to connect to Proxmox."

            # Check if the function signature includes 'node_name' and handle it
            sig = inspect.signature(func)
            if 'vm_id' in sig.parameters:
                if 'vm_id' not in kwargs:
                    if args:
                        kwargs['vm_id'] = args[0]
                        args = args[1:]
                    else:
                        logging.error("VM ID is required but not provided.")
                        return "VM ID is required."
            if 'node_name' in sig.parameters:
                if 'node_name' not in kwargs:
                    if args:
                        kwargs['node_name'] = args[0]
                        args = args[1:]
                    else:
                        # Attempt to use a default node_name from the session config if available
                        default_node_name = SessionConfig.get_node()
                        if default_node_name:
                            kwargs['node_name'] = default_node_name
                        else:
                            logging.error("Node name is required but not provided.")
                            return "Node name is required."

            # Ensure 'proxmox' is included for functions that require it
            if 'proxmox' in sig.parameters:
                kwargs['proxmox'] = proxmox

            # Add any missing parameters to the kwargs
            for param in sig.parameters:
                if param not in kwargs:
                    kwargs[param] = None

            # Append the remaining args to positional arguments
            logging.info(f"Executing {func.__name__} with adjusted args and kwargs.")
            try:
                return func(**kwargs)
            except TypeError as e:
                logging.error(f"TypeError when executing {func.__name__}: {e}")
                raise

        return wrapper

    return decorator

def update_wrapper_metadata(func, wrapper):
    wrapper.__description__ = getattr(func, '__description__', 'No description available.')
    wrapper.__command__ = getattr(func, '__command__', 'unknown')
    wrapper.__group__ = getattr(func, '__group__', 'default')
    wrapper.__params__ = getattr(func, '__params__', [])
    return wrapper
