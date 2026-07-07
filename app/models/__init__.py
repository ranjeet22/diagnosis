"""
Domain layer models and entities.
These define the core entities of the Diagnōsis platform, separated from DB or API shapes.
"""

class PatientRecord:
    """
    Example domain entity representing a single clinical patient profile.
    """
    def __init__(self, patient_id: str, age: int, gender: str) -> None:
        self.patient_id = patient_id
        self.age = age
        self.gender = gender
