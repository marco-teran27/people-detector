import asyncio
from viam.module.module import Module
from models.people_detector import PeopleDetector

if __name__ == '__main__':
    asyncio.run(Module.run_from_registry())
