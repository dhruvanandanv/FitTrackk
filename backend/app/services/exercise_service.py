from typing import List, Dict, Any, Optional

EXERCISE_CATALOG = [
    # Chest
    {
        "id": "bench-press",
        "name": "Barbell Bench Press",
        "category": "strength",
        "muscle_group": "Chest",
        "equipment": "Barbell",
        "instructions": "Lie flat on the bench, grip the barbell slightly wider than shoulder-width, lower the bar smoothly to mid-chest, and press firmly back up.",
    },
    {
        "id": "incline-dumbbell-press",
        "name": "Incline Dumbbell Press",
        "category": "strength",
        "muscle_group": "Chest",
        "equipment": "Dumbbells",
        "instructions": "Set the bench to a 30-45 degree angle. Press dumbbells upward with controlled descent to engage upper chest.",
    },
    {
        "id": "push-ups",
        "name": "Push-Ups",
        "category": "calisthenics",
        "muscle_group": "Chest",
        "equipment": "Bodyweight",
        "instructions": "Maintain a rigid plank posture, lower your chest close to the floor, and push up forcefully.",
    },

    # Back
    {
        "id": "deadlift",
        "name": "Barbell Deadlift",
        "category": "strength",
        "muscle_group": "Back / Posterior Chain",
        "equipment": "Barbell",
        "instructions": "Stand with feet hip-width apart. Hinge at the hips, grip the bar with a flat back, engage lats, and drive feet into the floor to stand upright.",
    },
    {
        "id": "pull-ups",
        "name": "Pull-Ups",
        "category": "calisthenics",
        "muscle_group": "Back",
        "equipment": "Pull-Up Bar",
        "instructions": "Grip the overhead bar slightly wider than shoulders. Pull up until chin clears the bar, lowering under full control.",
    },
    {
        "id": "barbell-row",
        "name": "Bent-Over Barbell Row",
        "category": "strength",
        "muscle_group": "Back",
        "equipment": "Barbell",
        "instructions": "Hinge forward with neutral spine. Pull bar towards lower abdomen, squeezing shoulder blades together at the apex.",
    },

    # Legs
    {
        "id": "squat",
        "name": "Barbell Back Squat",
        "category": "strength",
        "muscle_group": "Legs",
        "equipment": "Barbell",
        "instructions": "Rest barbell on upper traps. Squat down with knees tracking over toes until thighs are parallel or below, then drive up through midfoot.",
    },
    {
        "id": "romanian-deadlift",
        "name": "Romanian Deadlift (RDL)",
        "category": "strength",
        "muscle_group": "Legs / Hamstrings",
        "equipment": "Barbell / Dumbbells",
        "instructions": "Hinge backwards at the hips with soft knees, feel stretch in hamstrings, and contract glutes to return to standing.",
    },
    {
        "id": "lunges",
        "name": "Walking Lunges",
        "category": "strength",
        "muscle_group": "Legs",
        "equipment": "Dumbbells",
        "instructions": "Step forward into a 90-degree knee bend, maintain torso upright, and drive through front heel into the next step.",
    },

    # Shoulders
    {
        "id": "overhead-press",
        "name": "Overhead Barbell Press (OHP)",
        "category": "strength",
        "muscle_group": "Shoulders",
        "equipment": "Barbell",
        "instructions": "Stand tall with core braced. Press barbell overhead to full lockout without hyperextending lower back.",
    },
    {
        "id": "lateral-raise",
        "name": "Dumbbell Lateral Raise",
        "category": "strength",
        "muscle_group": "Shoulders",
        "equipment": "Dumbbells",
        "instructions": "Raise dumbbells out to sides until parallel to ground with a slight elbow bend to target lateral deltoids.",
    },

    # Arms
    {
        "id": "bicep-curl",
        "name": "Dumbbell Bicep Curl",
        "category": "strength",
        "muscle_group": "Arms",
        "equipment": "Dumbbells",
        "instructions": "Keep elbows close to torso, curl dumbbells up with controlled tempo, squeezing biceps at peak contraction.",
    },
    {
        "id": "tricep-dips",
        "name": "Tricep Dips",
        "category": "calisthenics",
        "muscle_group": "Arms",
        "equipment": "Parallel Bars",
        "instructions": "Lower body until elbows reach 90 degrees, keeping chest slightly upright, and push up using triceps.",
    },

    # Core
    {
        "id": "plank",
        "name": "Forearm Plank",
        "category": "core",
        "muscle_group": "Core",
        "equipment": "Bodyweight",
        "instructions": "Hold straight body line from head to heels with glutes and abs locked tight.",
    },
    {
        "id": "hanging-leg-raise",
        "name": "Hanging Leg Raise",
        "category": "core",
        "muscle_group": "Core",
        "equipment": "Pull-Up Bar",
        "instructions": "Hang from bar without swinging, raise legs to 90 degrees engaging lower abdominals.",
    },

    # Cardio
    {
        "id": "running",
        "name": "Outdoor Running / Jogging",
        "category": "cardio",
        "muscle_group": "Cardio / Full Body",
        "equipment": "Running Shoes",
        "instructions": "Maintain upright posture, light cadence, and rhythmic breathing across chosen distance or duration.",
    },
    {
        "id": "cycling",
        "name": "Road / Stationary Cycling",
        "category": "cardio",
        "muscle_group": "Cardio / Legs",
        "equipment": "Bicycle",
        "instructions": "Maintain smooth pedaling stroke at 80-90 RPM with consistent aerobic pacing.",
    },
    {
        "id": "rowing",
        "name": "Rowing Machine",
        "category": "cardio",
        "muscle_group": "Cardio / Full Body",
        "equipment": "Rower",
        "instructions": "Drive through legs first, lean torso slightly back, and pull handle into lower ribs.",
    },
    {
        "id": "jump-rope",
        "name": "Jump Rope",
        "category": "cardio",
        "muscle_group": "Cardio / Calves",
        "equipment": "Jump Rope",
        "instructions": "Stay on balls of feet, turn rope using wrists, and maintain light rhythmic hops.",
    },
]


class ExerciseService:
    @staticmethod
    def search_exercises(query: Optional[str] = None, muscle_group: Optional[str] = None) -> List[Dict[str, Any]]:
        results = EXERCISE_CATALOG

        if muscle_group:
            m_clean = muscle_group.lower()
            results = [e for e in results if m_clean in e["muscle_group"].lower()]

        if query:
            q_clean = query.lower().strip()
            results = [
                e for e in results
                if q_clean in e["name"].lower() or q_clean in e["muscle_group"].lower() or q_clean in e["category"].lower()
            ]

        return results
