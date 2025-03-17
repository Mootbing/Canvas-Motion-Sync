import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any, Optional
import datetime

class MotionHandler:
    """
    A class to handle interactions with the Motion API.
    """
    
    BASE_URL = "https://api.usemotion.com/v1"
    
    def __init__(self):
        """Initialize the MotionHandler with API credentials."""
        # Load environment variables from .env file
        dotenv_path = Path(__file__).parent.parent / '.env'
        load_dotenv(dotenv_path)
        
        # Get API key from environment variables
        self.api_key = os.getenv('MOTION_API_KEY')
        # Get workspace ID from environment variables
        self.workspace_id = os.getenv('MOTION_WORKSPACE_ID')

        if not self.api_key:
            raise ValueError("Motion API key not found in environment variables. Make sure MOTION_API_KEY is defined in your .env file.")
        
        if not self.workspace_id:
            raise ValueError("Motion workspace ID not found in environment variables. Make sure MOTION_WORKSPACE_ID is defined in your .env file.")
            
        # Set default headers for API requests
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def create_task(self, 
                   name: str, 
                   workspace_id: str, 
                   due_date: str = None, 
                   description: str = None, 
                   priority: str = "MEDIUM",
                   **kwargs) -> Dict[str, Any]:
        """
        Create a new task in Motion.
        
        Args:
            name: Task name
            workspace_id: ID of the workspace
            due_date: Due date in ISO 8601 format (e.g., "2025-03-20T10:00:00Z")
            description: Task description
            priority: Priority level (ASAP, HIGH, MEDIUM, or LOW)
            **kwargs: Additional task parameters
        
        Returns:
            Dictionary containing the API response
        
        Raises:
            Exception: If the API request fails
        """
        url = f"{self.BASE_URL}/tasks"
        
        # Build the request data
        data = {
            "name": name,
            "workspaceId": workspace_id,
            "duration": "NONE",
            "autoScheduled": {
                "startDate": datetime.datetime.now().isoformat(),
                "deadlineType": "HARD"
            }
        }
        
        # Add optional parameters if provided
        if due_date:
            data["dueDate"] = due_date
        if description:
            data["description"] = description
        if priority:
            data["priority"] = priority
            
        # Add any additional parameters
        data.update(kwargs)
        
        # Send the request
        response = requests.post(url, headers=self.headers, json=data)
        
        # Handle the response
        if response.status_code == 200:
            return response.json()
        else:
            error_message = f"Error creating task: {response.status_code} - {response.text}"
            raise Exception(error_message)
        
    def get_tasks(self):
        


# Example usage:
if __name__ == "__main__":
    try:
        # Create instance of MotionHandler
        motion = MotionHandler()
        
        # Example task creation
        result = motion.create_task(
            name="Test API Event",
            workspace_id=motion.workspace_id,  # Use the workspace ID from environment variables
            due_date="2025-03-20T10:00:00Z",
            description="This is a description for the new event.",
        )
        
        print("Task created successfully:", result)
        
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"Error: {e}")
