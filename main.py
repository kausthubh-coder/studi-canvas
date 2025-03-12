from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

app = FastAPI(title="Canvas API MCP Server")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CanvasResponse(BaseModel):
    success: bool
    data: Any
    error: Optional[str] = None

# Helper function to make Canvas API requests
async def canvas_request(institute_url: str, token: str, endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None):
    base_url = f"{institute_url}/api/v1/{endpoint}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        if method == "GET":
            response = requests.get(base_url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(base_url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(base_url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(base_url, headers=headers)
        
        response.raise_for_status()
        return CanvasResponse(success=True, data=response.json())
    except requests.exceptions.RequestException as e:
        return CanvasResponse(success=False, data=None, error=str(e))

# Courses endpoints
@app.get("/courses", response_model=CanvasResponse)
async def get_courses(
    institute_url: str = Query(..., description="Canvas institution URL (e.g., https://university.instructure.com)"),
    token: str = Query(..., description="Canvas API token"),
    enrollment_state: Optional[str] = Query("active", description="Filter by enrollment state")
):
    """Get all courses for the authenticated user"""
    return await canvas_request(
        institute_url=institute_url,
        token=token,
        endpoint="courses",
        params={"enrollment_state": enrollment_state}
    )

@app.get("/courses/{course_id}", response_model=CanvasResponse)
async def get_course(
    course_id: int,
    institute_url: str = Query(..., description="Canvas institution URL"),
    token: str = Query(..., description="Canvas API token")
):
    """Get details for a specific course"""
    return await canvas_request(
        institute_url=institute_url,
        token=token,
        endpoint=f"courses/{course_id}"
    )

# Assignments endpoints
@app.get("/courses/{course_id}/assignments", response_model=CanvasResponse)
async def get_assignments(
    course_id: int,
    institute_url: str = Query(..., description="Canvas institution URL"),
    token: str = Query(..., description="Canvas API token"),
    include: Optional[List[str]] = Query(None, description="Additional fields to include")
):
    """Get all assignments for a course"""
    params = {}
    if include:
        params["include"] = include
    
    return await canvas_request(
        institute_url=institute_url,
        token=token,
        endpoint=f"courses/{course_id}/assignments",
        params=params
    )

@app.get("/courses/{course_id}/assignments/{assignment_id}", response_model=CanvasResponse)
async def get_assignment(
    course_id: int,
    assignment_id: int,
    institute_url: str = Query(..., description="Canvas institution URL"),
    token: str = Query(..., description="Canvas API token")
):
    """Get details for a specific assignment"""
    return await canvas_request(
        institute_url=institute_url,
        token=token,
        endpoint=f"courses/{course_id}/assignments/{assignment_id}"
    )

# Missing assignments endpoint
@app.get("/missing_assignments", response_model=CanvasResponse)
async def get_missing_assignments(
    institute_url: str = Query(..., description="Canvas institution URL"),
    token: str = Query(..., description="Canvas API token")
):
    """Get all missing assignments across all active courses"""
    # First get all active courses
    courses_response = await canvas_request(
        institute_url=institute_url,
        token=token,
        endpoint="courses",
        params={"enrollment_state": "active"}
    )
    
    if not courses_response.success:
        return courses_response
    
    missing_assignments = []
    
    for course in courses_response.data:
        # Get assignments for each course
        assignments_response = await canvas_request(
            institute_url=institute_url,
            token=token,
            endpoint=f"courses/{course['id']}/assignments",
            params={"include": ["submission"]}
        )
        
        if not assignments_response.success:
            continue
        
        # Filter for missing assignments
        for assignment in assignments_response.data:
            if (
                'submission' in assignment 
                and assignment['submission'].get('missing', False)
            ):
                missing_assignments.append({
                    'course_name': course['name'],
                    'course_id': course['id'],
                    'assignment_name': assignment['name'],
                    'assignment_id': assignment['id'],
                    'due_date': assignment.get('due_at'),
                    'points_possible': assignment['points_possible']
                })
    
    return CanvasResponse(success=True, data=missing_assignments)

# Modules endpoints
@app.get("/courses/{course_id}/modules", response_model=CanvasResponse)
async def get_modules(
    course_id: int,
    institute_url: str = Query(..., description="Canvas institution URL"),
    token: str = Query(..., description="Canvas API token")
):
    """Get all modules for a course"""
    return await canvas_request(
        institute_url=institute_url,
        token=token,
        endpoint=f"courses/{course_id}/modules"
    )

@app.get("/courses/{course_id}/modules/{module_id}/items", response_model=CanvasResponse)
async def get_module_items(
    course_id: int,
    module_id: int,
    institute_url: str = Query(..., description="Canvas institution URL"),
    token: str = Query(..., description="Canvas API token")
):
    """Get all items in a module"""
    return await canvas_request(
        institute_url=institute_url,
        token=token,
        endpoint=f"courses/{course_id}/modules/{module_id}/items"
    )

# Files endpoints
@app.get("/courses/{course_id}/files", response_model=CanvasResponse)
async def get_course_files(
    course_id: int,
    institute_url: str = Query(..., description="Canvas institution URL"),
    token: str = Query(..., description="Canvas API token")
):
    """Get all files for a course"""
    return await canvas_request(
        institute_url=institute_url,
        token=token,
        endpoint=f"courses/{course_id}/files"
    )

# Announcements endpoint
@app.get("/courses/{course_id}/announcements", response_model=CanvasResponse)
async def get_announcements(
    course_id: int,
    institute_url: str = Query(..., description="Canvas institution URL"),
    token: str = Query(..., description="Canvas API token")
):
    """Get announcements for a course"""
    return await canvas_request(
        institute_url=institute_url,
        token=token,
        endpoint=f"courses/{course_id}/announcements"
    )

# Grades endpoint
@app.get("/courses/{course_id}/grades", response_model=CanvasResponse)
async def get_grades(
    course_id: int,
    institute_url: str = Query(..., description="Canvas institution URL"),
    token: str = Query(..., description="Canvas API token")
):
    """Get grades for a course"""
    return await canvas_request(
        institute_url=institute_url,
        token=token,
        endpoint=f"courses/{course_id}/grades"
    )

# Study guide generation endpoint (mock)
class StudyGuideRequest(BaseModel):
    course_id: int
    module_ids: Optional[List[int]] = None
    topic: Optional[str] = None

@app.post("/generate_study_guide", response_model=CanvasResponse)
async def generate_study_guide(
    request: StudyGuideRequest,
    institute_url: str = Query(..., description="Canvas institution URL"),
    token: str = Query(..., description="Canvas API token")
):
    """Generate a study guide based on course content"""
    # This would integrate with your LLM in a real implementation
    # Here we're just returning a mock response
    return CanvasResponse(
        success=True,
        data={
            "title": f"Study Guide for Course {request.course_id}",
            "sections": [
                {"title": "Key Concepts", "content": "This would contain key concepts from the course."},
                {"title": "Important Definitions", "content": "This would contain important definitions."},
                {"title": "Practice Questions", "content": "This would contain practice questions."}
            ]
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
