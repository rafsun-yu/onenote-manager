import types
from onm.cli.cli import launch

if __name__ == "__main__":
    obj = types.SimpleNamespace() # prepares context
    launch(obj=obj)