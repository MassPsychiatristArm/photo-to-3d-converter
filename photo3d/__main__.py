"""Allow ``python -m photo3d`` to behave like the ``photo3d`` console script."""
from photo3d.cli import app

if __name__ == "__main__":
    app()