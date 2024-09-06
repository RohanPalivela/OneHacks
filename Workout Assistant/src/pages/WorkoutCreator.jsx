import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import NavBar from "../components/nav-bar.jsx";

export default function WorkoutCreator() {
  const [age, setAge] = useState('');
  const [sex, setSex] = useState('');
  const [weight, setWeight] = useState('');
  const [height, setHeight] = useState('');
  const [freeTime, setFreeTime] = useState('');
  const [goals, setGoals] = useState([]);
  const [mealImages, setMealImages] = useState({});
  const [dietRecommendations, setDietRecommendations] = useState({});
  const [workoutRecommendations, setWorkoutRecommendations] = useState({});

  const handleGoalChange = (goal) => {
    setGoals((prev) =>
      prev.includes(goal) ? prev.filter((g) => g !== goal) : [...prev, goal]
    );
  };

  const handleImageUpload = (meal, e) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setMealImages((prev) => ({ ...prev, [meal]: reader.result }));
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();

    ['breakfast', 'lunch', 'dinner'].forEach((meal) => {
      if (mealImages[meal]) {
        formData.append(meal, mealImages[meal]);
      }
    });

    formData.append('age', age);
    formData.append('sex', sex);
    formData.append('weight', weight);
    formData.append('height', height);
    formData.append('freeTime', freeTime);
    formData.append('goals', JSON.stringify(goals));

    try {
      const response = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setDietRecommendations(data);
        console.log("Diet Recommendations:", dietRecommendations);
      } else {
        console.error("Server responded with an error:", response.status);
      }
    } catch (error) {
      console.error("There was an error submitting the form:", error);
    }

    try {
      const response = await fetch('http://localhost:5000/workout', {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setWorkoutRecommendations(data);
      } else {
        console.error("Server responded with an error:", response.status);
      }
    } catch (error) {
      console.error("There was an error submitting the form:", error);
    }
  };

  return (
    <>
      <NavBar />
      <div className="flex flex-col min-h-screen">
        <main className="flex-grow flex flex-col md:flex-row">
          <div className="md:w-1/2 p-4 bg-muted">
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="age">Age</Label>
                  <Input id="age" value={age} onChange={(e) => setAge(e.target.value)} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="sex">Sex</Label>
                  <Select onValueChange={setSex}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select sex" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="male">Male</SelectItem>
                      <SelectItem value="female">Female</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="weight">Weight (pounds)</Label>
                  <Input id="weight" value={weight} onChange={(e) => setWeight(e.target.value)} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="height">Height (inches)</Label>
                  <Input id="height" value={height} onChange={(e) => setHeight(e.target.value)} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="freeTime">Free time today (mins)</Label>
                  <Input id="freeTime" value={freeTime} onChange={(e) => setFreeTime(e.target.value)} />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Goals</Label>
                <div className="flex flex-wrap gap-4">
                  {['Lose weight', 'Gain muscle', 'Improve endurance', 'Increase flexibility'].map((goal) => (
                    <div key={goal} className="flex items-center space-x-2">
                      <Checkbox id={goal} checked={goals.includes(goal)} onCheckedChange={() => handleGoalChange(goal)} />
                      <label htmlFor={goal}>{goal}</label>
                    </div>
                  ))}
                </div>
              </div>
              <div className="space-y-4">
                {['breakfast', 'lunch', 'dinner'].map((meal) => (
                  <div key={meal} className="space-y-2">
                    <Label htmlFor={`${meal}-image`}>{`${meal.charAt(0).toUpperCase() + meal.slice(1)} Image`}</Label>
                    <Input id={`${meal}-image`} type="file" accept="image/*" onChange={(e) => handleImageUpload(meal, e)} />
                    {mealImages[meal] && (
                      <img src={mealImages[meal]} alt={`${meal} meal`} className="w-full h-40 object-cover rounded-md" />
                    )}
                  </div>
                ))}
              </div>
              <Button type="submit" className="w-full">Generate Recommendations</Button>
            </form>
          </div>
          <div className="md:w-1/2 p-4 bg-background">
            <div className="space-y-4">
              <h2 className="text-xl font-semibold mb-2">Diet Recommendations</h2>
              <div className="bg-muted p-4 rounded-md">
                {Object.keys(dietRecommendations).length > 0 ? (
                  Object.keys(dietRecommendations).map((meal) => {
                    if (meal === "rating") return null; // Skip rating in display
                    const recommendations = dietRecommendations[meal];
                    return (
                      <div key={meal} className="mb-4">
                        <h3 className="text-lg font-semibold">{meal.charAt(0).toUpperCase() + meal.slice(1)}</h3>
                        <p><strong>Calories:</strong> {recommendations?.Calories || 'N/A'}</p>
                        <p><strong>Suggestions:</strong></p>
                        <ul className="list-disc pl-5">
                        {Array.isArray(recommendations?.Suggestion) && recommendations.Suggestion.length > 0 ? (
                          recommendations.Suggestion.map((suggestion, index) => (
                            <li key={index}>{suggestion}</li>
                          ))
                        ) : (
                          <li>No suggestions available.</li>
                        )}
                        </ul>
                        <p><strong>Nutrition:</strong></p>
                        <ul className="list-disc pl-5">
                          {recommendations?.Nutrition ? (
                            Object.entries(recommendations.Nutrition).map(([key, value]) => (
                              <li key={key}><strong>{key}:</strong> {value}</li>
                            ))
                          ) : (
                            <li>No nutritional information available.</li>
                          )}
                        </ul>
                      </div>
                    );
                  })
                ) : (
                  <p>No diet recommendations available yet.</p>
                )}
              </div>
              <div>
                <h2 className="text-xl font-semibold mb-2">Workout Recommendations</h2>
                <div className="bg-muted p-4 rounded-md">
                  {Object.keys(workoutRecommendations).length > 0 ? (
                    Object.keys(workoutRecommendations).map((section) => {
                      const sectionData = workoutRecommendations[section];
                      return (
                        <div key={section} className="mb-4">
                          <h3 className="text-lg font-semibold">{section.replace('_', ' ').toUpperCase()}</h3>
                          <p><strong>Duration:</strong> {sectionData.duration} minutes</p>
                          <p><strong>Exercises:</strong></p>
                          <ul className="list-disc pl-5">
                            {sectionData.exercises.map((exercise, index) => (
                              <li key={index}>
                                <strong>{exercise.name}</strong> - Duration: {exercise.duration} mins
                                {exercise.sets && `, Sets: ${exercise.sets}`}
                                {exercise.reps_per_set && `, Reps per set: ${exercise.reps_per_set}`}
                                {exercise.calories_burned && `, Calories burned: ${exercise.calories_burned}`}
                              </li>
                            ))}
                          </ul>
                        </div>
                      );
                    })
                  ) : (
                    <p>No workout recommendations available yet.</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </>
  );
}
