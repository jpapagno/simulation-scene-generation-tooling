"""Launch an empty Isaac Lab simulation and keep it running.

Thin entry point kept for the Isaac Lab ``-p <script>`` workflow, e.g.::

    ./isaaclab.bat -p scripts/launch_simulation.py

The implementation lives in the installed ``scenegen`` package; prefer
the ``scenegen`` console script (``pip install -e .`` then ``scenegen``).
"""

from scenegen.cli import main

if __name__ == "__main__":
    main()
