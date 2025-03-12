import requests
import json
from pprint import pprint

# Test configuration
BASE_URL = "http://localhost:8000"
INSTITUTE_URL = "https://uncg.instructure.com"  # Replace with your institution's Canvas URL
TOKEN = "1398~WHKYFYxLyeThzEWwUv6TwPT3eJPhGYwfGHYRDcLJhzUuzkvKuTH323kntNFPGfmy"  # Replace with your Canvas API token

def test_endpoint(endpoint, params=None, method="GET", data=None):
    """Test an API endpoint and print the results"""
    url = f"{BASE_URL}/{endpoint}"
    
    # Add common parameters
    if params is None:
        params = {}
    params["institute_url"] = INSTITUTE_URL
    params["token"] = TOKEN
    
    print(f"\n{'='*50}")
    print(f"Testing: {method} {endpoint}")
    print(f"{'='*50}")
    
    try:
        if method == "GET":
            response = requests.get(url, params=params)
        elif method == "POST":
            response = requests.post(url, params=params, json=data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['success']}")
            
            if result['success']:
                if isinstance(result['data'], list):
                    print(f"Found {len(result['data'])} items")
                    if len(result['data']) > 0:
                        print("\nFirst item:")
                        pprint(result['data'][0])
                else:
                    print("\nData:")
                    pprint(result['data'])
            else:
                print(f"Error: {result['error']}")
        else:
            print(f"Error: {response.text}")
    
    except Exception as e:
        print(f"Exception: {str(e)}")

def run_tests():
    """Run tests for various endpoints"""
    print("\nStarting Canvas API Tests")
    print("-------------------------")
    
    # Test courses endpoint
    test_endpoint("courses")
    
    # Get the first course ID for further tests
    response = requests.get(
        f"{BASE_URL}/courses",
        params={"institute_url": INSTITUTE_URL, "token": TOKEN}
    )
    
    if response.status_code == 200 and response.json()['success']:
        courses = response.json()['data']
        if courses:
            course_id = courses[0]['id']
            
            # Test course details
            test_endpoint(f"courses/{course_id}")
            
            # Test assignments
            test_endpoint(f"courses/{course_id}/assignments")
            
            # Test modules
            test_endpoint(f"courses/{course_id}/modules")
            
            # Test missing assignments
            test_endpoint("missing_assignments")
            
            # Test study guide generation
            test_endpoint(
                "generate_study_guide", 
                method="POST",
                data={"course_id": course_id}
            )
    
    print("\nTests completed!")

if __name__ == "__main__":
    run_tests() 