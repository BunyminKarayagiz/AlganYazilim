import asyncio
import random

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
            print(f"Estimated Position Received: {self.estimated_position}")
            await asyncio.sleep(1)  # Simulate delay in receiving data

    async def camera_receiver(self):
        """Simulate receiving live camera data asynchronously."""
        while True:
            # Simulate receiving data from the live camera system
            self.camera_position = {
                "x": random.uniform(0, 1920),
                "y": random.uniform(0, 1080),
            }
            print(f"Camera Position Received: {self.camera_position}")
            await asyncio.sleep(0.1)  # Simulate delay in receiving data

    async def air_defence_receiver(self):
        while True:
            # Simulate receiving data from the live camera system
            self.hss_coord = {
                "relative_x": random.uniform(0, 1920),
                "relative_y": random.uniform(0, 1080),
                "danger": bool(random.randint(0,1)) 
            }
            print(f"HSS: {self.hss_coord}")
            await asyncio.sleep(1)  # Simulate delay in receiving data

    def make_decision(self):
        """Make a decision based on the received data."""
        if self.estimated_position and self.camera_position:
            # Example decision-making logic: simple proximity check
            if abs(self.estimated_position["latitude"]) < 10 and abs(self.camera_position["x"] - 960) < 100:
                print("Enemy locked and ready to shoot!")
            else:
                print("Tracking enemy...")

    async def run_system(self):
        """Run the UAV system."""
        position_task = asyncio.create_task(self.position_receiver())
        camera_task = asyncio.create_task(self.camera_receiver())
        hss_task = asyncio.create_task(self.air_defence_receiver())

        while True:
            self.make_decision()
            await asyncio.sleep(0.05)  # Adjust the frequency of decision-making

if __name__ == "__main__":
    uav_system = UAVSystem()
    asyncio.run(uav_system.run_system())
