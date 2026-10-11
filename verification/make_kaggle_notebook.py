#!/usr/bin/env python3
import json
from pathlib import Path

notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# MERENVAY ARC-AGI-2 offline verification candidate\n",
                "This notebook uses attached inputs only and makes no hidden-set performance claim."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "from pathlib import Path\n",
                "import subprocess\n",
                "entries = sorted(Path('/kaggle/input').glob('**/kaggle_entry.py'))\n",
                "if not entries:\n",
                "    raise FileNotFoundError('Attach the MERENVAY offline bundle dataset')\n",
                "entry = entries[0]\n",
                "print('Using entry:', entry)\n",
                "subprocess.run(['python', str(entry)], check=True)\n",
                "assert Path('/kaggle/working/submission.json').exists()\n",
                "print('submission.json ready')\n"
            ]
        }
    ],
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.13"}
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

Path("verification/kaggle_submission.ipynb").write_text(
    json.dumps(notebook, indent=2), encoding="utf-8"
)
print("verification/kaggle_submission.ipynb")
