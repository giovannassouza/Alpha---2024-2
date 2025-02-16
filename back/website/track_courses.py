from flask import Blueprint, session, request, make_response
from .json_responses import successful_response, error_response

track_courses = Blueprint('track_courses', __name__)

@track_courses.route('/courses/set-current', methods=['POST'])
def set_current_course():
    """
    Endpoint to set the current course of the user.
    ---
    tags:
      - Courses
    parameters:
      - name: course_id
        in: body
        type: int
        required: true
        description: The ID of the course.
    responses:
      200:
        description: Current course set successfully.
        schema:
          type: object
          properties:
            message:
              type: string
              description: Success message.
      400:
        description: Course ID not provided.
    """
    data = request.get_json()
    course_id = data.get('course_id')
    if not course_id:
        return error_response(description='Course ID not provided', response=400)
    
    # Store course_id in cookies
    response = make_response(successful_response(description='Current course set successfully'))
    response.set_cookie('current_course', str(course_id))
    return response

@track_courses.route('/courses/get-current', methods=['GET'])
def get_current_course():
    """
    Endpoint to get the current course of the user.
    ---
    tags:
      - Courses
    responses:
      200:
        description: Current course obtained successfully.
        schema:
          type: object
          properties:
            message:
              type: string
              description: Success message.
            course_id:
              type: int
              description: ID of the current course.
      400:
        description: Current course not set.
    """
    course_id = request.cookies.get('current_course')
    if not course_id:
        return error_response(description='Current course not set', response=400)
    
    return successful_response(
        description='Current course obtained successfully', 
        data={'course_id': course_id}
    )