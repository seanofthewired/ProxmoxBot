class SessionConfig:
    _current_node = None

    @classmethod
    def set_node(cls, node_name):
        """Set the current node name."""
        cls._current_node = node_name

    @classmethod
    def get_node(cls):
        """Get the current node name."""
        return cls._current_node
