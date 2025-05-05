import asyncio

from viam.module.module import Module
from models.people_detector import PeopleDetector

"""
Main Module for People Detector Service
=====================================

This is the entry point for the People Detector modular service for Viam's robotics platform.
It registers and runs the PeopleDetector component with Viam's module registry system.

The module uses Viam's module system to:
1. Register the PeopleDetector component
2. Handle component lifecycle
3. Manage communication with viam-server
"""

if __name__ == '__main__':
    """
    Entry point for the module.
    
    Executes:
    1. Initializes the async runtime
    2. Registers PeopleDetector with Viam's module registry
    3. Starts the module process
    
    The Module.run_from_registry() method:
    - Handles component registration
    - Manages module lifecycle
    - Establishes communication with viam-server
    - Processes incoming requests
    """
    asyncio.run(Module.run_from_registry())
