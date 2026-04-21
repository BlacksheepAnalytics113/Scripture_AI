"""
Real time audio captures: Basically captures audio from the default microphone in chunks and yeilds them as a numpy arrays for transacription
"""

import asyncio
import logging
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
import tempfile
import os

