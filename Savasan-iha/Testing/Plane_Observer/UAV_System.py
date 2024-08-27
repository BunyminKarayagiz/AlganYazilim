import asyncio
import random
import time

class UAVSystem:
    def __init__(self):
        self.estimated_position = None
        self.camera_position = None

    async def position_receiver(self):
        """Simulate receiving estimated position data asynchronously."""
        while True:
            # Simulate receiving data from the estimation system
            self.estimated_position = {
                "latitude": random.uniform(-90, 90),
                "longitude": random.uniform(-180, 180),
            }
            await asyncio.sleep(1)  # Simulate delay in receiving data

    async def camera_receiver(self):
        """Simulate receiving live camera data asynchronously."""
        while True:
            # Simulate receiving data from the live camera system
            self.camera_position = {
                "x": random.uniform(0, 1920),
                "y": random.uniform(0, 1080),
            }
            await asyncio.sleep(0.1)  # Simulate delay in receiving data

    async def run_system(self):
        """Run the UAV system."""
        position_task = asyncio.create_task(self.position_receiver())
        camera_task = asyncio.create_task(self.camera_receiver())
        
        await asyncio.gather(position_task, camera_task)

if __name__ == "__main__":
    uav_system = UAVSystem()
    asyncio.run(uav_system.run_system())
    while True:
        print("AFTER ASYNC")