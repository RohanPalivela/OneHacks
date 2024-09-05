"use client"

import { useEffect, useRef, useState,  } from 'react'
import { Toggle } from "@/components/ui/toggle.jsx"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Camera} from "lucide-react"
import NavBar from "../components/nav-bar.jsx"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import FrameDisplay from "../components/video-frame.jsx"
import ResetButton from "../components/reset-button.jsx"
import { Input } from '@/components/ui/input.jsx'

export default function RepTracker() {
  const [isCameraOn, setIsCameraOn] = useState(false)
  const [workout, setWorkout] = useState("empty");
  const [reps, setReps] = useState(5);
  const [goalReps, setGoalReps] = useState(999999999);
  const [concentric, setConcentric] = useState(true);
  const [sets, setSets] = useState(0);
  const [intervalId, setIntervalId] = useState(null); // Store the interval ID

  const videoConstraints = {
    facingMode: "user",
  };
  
  const toggleCamera = () => {
    if (isCameraOn) {
      setIsCameraOn(false)
    } else {
      setIsCameraOn(true)
    }
  }

  const reset = () => {
    setReps(0);
    setSets(Math.max(sets - 1, 0));
    setConcentric(true);

    console.log("New reps: " + reps);
  }

  const workoutChosen = async (value) => {
    setWorkout(value);
  }

  useEffect(() => {
    // Clear the previous interval when workout changes or component unmounts
    if (intervalId) {
      clearInterval(intervalId);
      setIntervalId(null);
    }

    if (workout && workout !== 'empty') {
      // Start a new interval when a workout is selected
      const newIntervalId = setInterval(async () => {
        try {
          // Dynamically create the API endpoint based on the workout name
          const response = await fetch(`http://127.0.0.1:5000/get${workout}`);
          
          // Assuming the response contains a JSON with an 'efficiency' field
          
          const data = await response.json();
          console.log(data);
          const efficiency = data.efficiency;

          console.log(`Efficiency for ${workout}: ${efficiency}%`);

          // Increment reps if efficiency reaches or exceeds 80%
          if (efficiency >= 80) {
            setReps(prevReps => prevReps + 1);
          }
        } catch (error) {
          console.error("Error fetching efficiency:", error);
        }
      }, 2000); // Poll the API every 2 seconds (adjust as needed)

      // Store the new interval ID so it can be cleared later
      setIntervalId(newIntervalId);
    }

    // Cleanup function to clear the interval when component unmounts or workout changes
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [workout]); // Re-run the effect whenever workout changes

  return (
    <>
        <NavBar/>
        <main className="flex-grow flex w-screen">
            <div className="overflow-hidden w-3/4 bg-muted ml-4 flex items-center justify-center">
            {isCameraOn ? (
              <FrameDisplay />
            ) : (
                <div className="text-center">
                <Camera className="h-16 w-16 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">Camera is off</p>
                </div>
            )}
            </div>
            <Toggle className="absolute right-1/4 top-[9vh] bg-background" variant="primary" onClick={toggleCamera}>
                <Camera className="h-4 w-4 rounded-full" />
            </Toggle>
            <div className="w-1/4 bg-background px-4">
            <ScrollArea className="h-[calc(100vh-5rem)] border px-4 ">
                <h2 className="text-lg font-semibold my-4">Information</h2>
                <p className="mb-4">Choose an exercise from the dropdown and begin doing reps.</p>
                <p className="mb-4">Here are some tips before you get started!</p>
                <ul className="list-disc pl-5 mb-4">
                  <li>Focus on the stretched portion of the lift</li>
                  <li>Lift close to or until failure of technique</li>
                  <li>Always prioritize recovery!</li>
                </ul>
                <div className='flex justify-center'>
                  <div className="w-[95%]">
                    <Select onValueChange={workoutChosen}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select Workout" />
                      </SelectTrigger>
                      <SelectContent>
                      <SelectItem value="empty">Select Item</SelectItem>
                        <SelectItem value="Curl">Curl</SelectItem>
                        <SelectItem value="Squat">Squat</SelectItem>
                        <SelectItem value="Pullup">Pullup</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <h2 className="text-lg font-semibold mt-[5rem] mb-4">Choose Exercise</h2>
                {(workout !== "empty") ? (
                  <>
                    <p className='text-lg font-medium my-4'> {workout}</p>
                    <div className="flex flex-row justify-center items-center mb-4">
                      <div className="w-[45%]">
                        <Input type="number" onChange={(val) => {setSets(Math.max(val.target.value, 0)); setReps(0);}} placeholder="Sets" />
                      </div>
                      <p className='px-2'>x</p>
                      <div className="w-[45%]">
                        <Input type="number" onChange={(val) => {setGoalReps(val.target.value)}} 
                          placeholder="Reps" />
                      </div>
                    </div>
                    <p className='mb-4'>{sets} more sets left!</p>
                    <div className="mb-4 flex flex-row justify-between items-center">
                      <p className="w-3/4">Your Reps</p>
                      <p> {reps} </p>
                      <ResetButton onClick={reset}/>
                    </div> 
                    {(reps >= goalReps || sets == 0) ? (
                      <>
                        <p className="text-green-500 mb-4"> You have reached your goal! Once you hit reset, your reps will reset and your sets will decrement. </p>
                        <p className="text-green-500">If you have done all your sets, feel free to do another exercise.</p>
                      </>
                    ) : (
                      <p> Keep going! You are almost at your goal!</p>
                    )}
                    
                  </>
                ) : (
                    <p className='py-5'> Choose an option to get started!</p>
                )}
            </ScrollArea>
                
            </div>
        </main>
    </>
    
  )
}