import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import NavBar from "../components/nav-bar.jsx"
import axios from 'axios';

export default function WorkoutCreator() {
  const [age, setAge] = useState('');
  const [sex, setSex] = useState('');
  const [weight, setWeight] = useState('');
  const [height, setHeight] = useState('');
  const [freeTime, setFreeTime] = useState('');
  const [goals, setGoals] = useState([]);
  const [mealImages, setMealImages] = useState({});
  const [dietRecommendations, setDietRecommendations] = useState('');
  const [workoutRecommendations, setWorkoutRecommendations] = useState('');

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
    // Here you would typically send the data to a backend API
    // For this example, we'll just set some placeholder recommendations

    
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
    const response = await axios.post('http://127.0.0.1:5000/predict', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    // Assuming the response contains diet and workout recommendations
    // setDietRecommendations(response.json);
    // setWorkoutRecommendations(response.json);
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
            <div>
              <h2 className="text-xl font-semibold mb-2">Diet Recommendations</h2>
              <p className="bg-muted p-4 rounded-md">{dietRecommendations || "Submit your information to get diet recommendations."}</p>
            </div>
            <div>
              <h2 className="text-xl font-semibold mb-2">Workout Recommendations</h2>
              <p className="bg-muted p-4 rounded-md">{workoutRecommendations || "Submit your information to get workout recommendations."}</p>
            </div>
          </div>
        </div>
      </main>
    </div>
    </>
  );
}
