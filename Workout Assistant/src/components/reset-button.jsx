import React from "react";
import { RotateCcw } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function ResetButton({ onClick } ) {
  return (
    <Button onClick={onClick} variant="ghost" size="icon">
      <RotateCcw className="h-4 w-4" />
      <span className="sr-only">Reset</span>
    </Button>
  );
}