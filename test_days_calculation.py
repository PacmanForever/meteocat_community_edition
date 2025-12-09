
from unittest.mock import MagicMock

# Mock constants
MODE_ESTACIO = "estacio"
MODE_MUNICIPI = "municipi"

class MockCoordinator:
    def __init__(self):
        self.data = {"quotes": {"plans": []}}
        self.update_time_1 = "06:00"
        self.update_time_2 = "14:00"
        self.update_time_3 = ""
        self.enable_forecast_daily = True
        self.enable_forecast_hourly = False

class MockSensor:
    def __init__(self, coordinator, plan_name, mode):
        self.coordinator = coordinator
        self._plan_name = plan_name
        self._mode = mode
        
    @property
    def native_value(self):
        available = 1000 # Mock available
        
        # Calculate updates per day based on configuration
        updates_per_day = 0
        if self.coordinator.update_time_1:
            updates_per_day += 1
        if self.coordinator.update_time_2:
            updates_per_day += 1
        if self.coordinator.update_time_3:
            updates_per_day += 1
            
        calls_per_update = 0
        plan_name_lower = self._plan_name.lower()
        
        print(f"Plan: {self._plan_name}, Mode: {self._mode}")
        print(f"Updates per day: {updates_per_day}")
        
        if "xema" in plan_name_lower:
            if self._mode == MODE_ESTACIO:
                calls_per_update = 1
                print("Matched XEMA logic")
        elif "predicci" in plan_name_lower:
            if self.coordinator.enable_forecast_daily:
                calls_per_update += 1
            if self.coordinator.enable_forecast_hourly:
                calls_per_update += 1
            print(f"Matched Predicció logic. Calls: {calls_per_update}")
        elif "quota" in plan_name_lower:
            calls_per_update = 1
            
        daily_consumption = updates_per_day * calls_per_update
        print(f"Daily consumption: {daily_consumption}")
        
        if daily_consumption == 0:
            return 9999 # Infinite
            
        return round(available / daily_consumption, 1)

# Test cases
coordinator = MockCoordinator()

print("--- Test 1: Station Mode, XEMA Plan ---")
s1 = MockSensor(coordinator, "XEMA", MODE_ESTACIO)
print(f"Result: {s1.native_value}")

print("\n--- Test 2: Municipality Mode, XEMA Plan ---")
s2 = MockSensor(coordinator, "XEMA", MODE_MUNICIPI)
print(f"Result: {s2.native_value}")

print("\n--- Test 3: Municipality Mode, Predicció Plan ---")
s3 = MockSensor(coordinator, "Predicció", MODE_MUNICIPI)
print(f"Result: {s3.native_value}")

print("\n--- Test 4: Station Mode, Predicció Plan ---")
s4 = MockSensor(coordinator, "Predicció", MODE_ESTACIO)
print(f"Result: {s4.native_value}")

print("\n--- Test 5: Station Mode, Referència Plan ---")
s5 = MockSensor(coordinator, "Referència", MODE_ESTACIO)
print(f"Result: {s5.native_value}")
