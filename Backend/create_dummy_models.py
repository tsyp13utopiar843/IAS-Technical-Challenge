import pickle
import os
import random

# Define dummy model classes that mimic the expected interface
class DummyHazardModel:
    def predict(self, data):
        # Randomly return Safe or Hazard based on telemetry
        # Expecting dict with vibration, temp, etc.
        return "Hazard" if random.random() < 0.1 else "Safe"

class DummyPPEModel:
    def predict(self, data):
        # Randomly return Safe or Violation based on sensor data
        # Expecting dict with 'sensors' list
        return "Violation" if random.random() < 0.1 else "Safe"

class DummyCyberModel:
    def predict(self, data):
        # Randomly return Normal or DDoS
        return "DDoS" if random.random() < 0.05 else "Normal"

class DummyMaintModel:
    def predict(self, data):
        # Return a random RUL between 0 and 100
        return random.randint(0, 100)

class DummyEnergyModel:
    def predict(self, data):
        # Return a random optimization suggestion
        return "Reduce Load" if random.random() < 0.2 else "Optimal"

def create_models():
    models = {
        "agents/safety/artifacts/hazard_model.pkl": DummyHazardModel(),
        "agents/ppe/artifacts/ppe_model.pkl": DummyPPEModel(),
        "agents/cyber/artifacts/model.pkl": DummyCyberModel(),
        "agents/maint/artifacts/model.pkl": DummyMaintModel(),
        "agents/energy/artifacts/model.pkl": DummyEnergyModel(),
    }

    for path, model in models.items():
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(model, f)
        print(f"Created {path}")

if __name__ == "__main__":
    create_models()
