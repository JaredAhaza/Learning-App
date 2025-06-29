# Learning App API Documentation

## Base URL
```
http://localhost:8000/api/
```

## Authentication

### Login
**POST** `/auth/login/`

**Request Body:**
```json
{
    "username": "student_username",
    "password": "password"
}
```

**Response:**
```json
{
    "user_type": "student",
    "user_id": 1,
    "username": "student_username",
    "student_id": "STU001"
}
```

## Students

### Get All Students
**GET** `/students/`

**Response:**
```json
[
    {
        "student_id": "STU001",
        "email": "student@example.com",
        "user": {
            "id": 1,
            "username": "student_username",
            "email": "student@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "date_joined": "2024-01-01T00:00:00Z"
        }
    }
]
```

### Get Student Details
**GET** `/students/{student_id}/`

**Response:**
```json
{
    "student_id": "STU001",
    "email": "student@example.com",
    "user": {
        "id": 1,
        "username": "student_username",
        "email": "student@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "date_joined": "2024-01-01T00:00:00Z"
    },
    "profile": {
        "id": 1,
        "student": {...},
        "profile_picture": "/media/profile_pictures/student.jpg",
        "phone_number": "+1234567890",
        "date_of_birth": "1990-01-01",
        "bio": "Student bio",
        "gender": "M"
    }
}
```

### Get Student Enrollments
**GET** `/students/{student_id}/enrollments/`

### Get Student Units
**GET** `/students/{student_id}/units/`

### Get Student Lessons
**GET** `/students/{student_id}/lessons/`

## Teachers

### Get All Teachers
**GET** `/teachers/`

### Get Teacher Details
**GET** `/teachers/{teacher_id}/`

### Get Teacher Units
**GET** `/teachers/{teacher_id}/units/`

### Get Teacher Lessons
**GET** `/teachers/{teacher_id}/lessons/`

## Courses

### Get All Courses
**GET** `/courses/`

**Response:**
```json
[
    {
        "course_id": "CS101",
        "course_name": "Introduction to Computer Science",
        "course_code": "CS101",
        "description": "Basic computer science concepts",
        "instructions": "Course instructions",
        "credits": 3
    }
]
```

### Get Course Details
**GET** `/courses/{course_id}/`

## Cohorts

### Get All Cohorts
**GET** `/cohorts/`

**Response:**
```json
[
    {
        "cohort_id": "COH001",
        "course": {
            "course_id": "CS101",
            "course_name": "Introduction to Computer Science",
            "course_code": "CS101",
            "description": "Basic computer science concepts",
            "instructions": "Course instructions",
            "credits": 3
        },
        "name": "Fall 2024",
        "start_date": "2024-09-01",
        "end_date": "2024-12-31"
    }
]
```

### Get Cohort Students
**GET** `/cohorts/{cohort_id}/students/`

## Units

### Get All Units
**GET** `/units/`

**Query Parameters:**
- `cohort`: Filter by cohort ID
- `teacher`: Filter by teacher ID

### Get Unit Details
**GET** `/units/{unit_id}/`

### Get Unit Lessons
**GET** `/units/{unit_id}/lessons/`

## Lessons

### Get All Lessons
**GET** `/lessons/`

**Query Parameters:**
- `unit`: Filter by unit ID
- `teacher`: Filter by teacher ID
- `class_type`: Filter by class type (LECTURE, LAB, TUTORIAL)

### Get Lesson Details
**GET** `/lessons/{lesson_id}/`

### Get Lesson Topics
**GET** `/lessons/{lesson_id}/topics/`

### Get Lesson Quiz
**GET** `/lessons/{lesson_id}/quiz/`

## Topics

### Get All Topics
**GET** `/topics/`

**Query Parameters:**
- `lesson`: Filter by lesson ID

### Get Topic Details
**GET** `/topics/{topic_id}/`

## Quizzes

### Get All Quizzes
**GET** `/quizzes/`

### Get Quiz Details
**GET** `/quizzes/{quiz_id}/`

### Submit Quiz
**POST** `/quizzes/{quiz_id}/submit/`

**Request Body:**
```json
{
    "student_id": "STU001",
    "answers": [
        {
            "question_id": 1,
            "selected_answer_id": 2,
            "text_answer": null
        },
        {
            "question_id": 2,
            "selected_answer_id": null,
            "text_answer": "My explanation answer"
        }
    ]
}
```

## Questions

### Get All Questions
**GET** `/questions/`

**Query Parameters:**
- `quiz`: Filter by quiz ID

### Get Question Details
**GET** `/questions/{question_id}/`

## Quiz Submissions

### Get All Quiz Submissions
**GET** `/quiz-submissions/`

**Query Parameters:**
- `student`: Filter by student ID
- `quiz`: Filter by quiz ID

### Get Quiz Submission Details
**GET** `/quiz-submissions/{submission_id}/`

## Projects

### Get All Projects
**GET** `/projects/`

**Query Parameters:**
- `lesson`: Filter by lesson ID

### Get Project Details
**GET** `/projects/{project_id}/`

## Project Submissions

### Get All Project Submissions
**GET** `/project-submissions/`

**Query Parameters:**
- `project`: Filter by project ID
- `student`: Filter by student ID

### Get Project Submission Details
**GET** `/project-submissions/{submission_id}/`

## Progress Tracking

### Lesson Progress
**GET** `/lesson-progress/`

**Query Parameters:**
- `student`: Filter by student ID
- `lesson`: Filter by lesson ID

### Topic Progress
**GET** `/topic-progress/`

**Query Parameters:**
- `student`: Filter by student ID
- `topic`: Filter by topic ID

## Online Classes

### Get All Online Classes
**GET** `/online-classes/`

**Query Parameters:**
- `unit`: Filter by unit ID

### Get Online Class Details
**GET** `/online-classes/{class_id}/`

## Time Slots

### Get All Time Slots
**GET** `/time-slots/`

**Query Parameters:**
- `teacher`: Filter by teacher ID
- `lesson`: Filter by lesson ID
- `day`: Filter by day of week

### Get Time Slot Details
**GET** `/time-slots/{slot_id}/`

## Dashboard

### Student Dashboard
**GET** `/dashboard/student/{student_id}/`

**Response:**
```json
{
    "student_id": "STU001",
    "email": "student@example.com",
    "user": {...},
    "profile": {...},
    "enrollments": [...]
}
```

### Teacher Dashboard
**GET** `/dashboard/teacher/{teacher_id}/`

## Enrollments

### Get All Enrollments
**GET** `/enrollments/`

**Query Parameters:**
- `student`: Filter by student ID
- `cohort`: Filter by cohort ID
- `status`: Filter by status (active, inactive, completed)

### Get Enrollment Details
**GET** `/enrollments/{enrollment_id}/`

## Enrollment Requests

### Get All Enrollment Requests
**GET** `/enrollment-requests/`

**Query Parameters:**
- `student`: Filter by student ID
- `cohort`: Filter by cohort ID
- `status`: Filter by status (pending, approved, rejected)

### Get Enrollment Request Details
**GET** `/enrollment-requests/{request_id}/`

## Common Response Formats

### Success Response
```json
{
    "id": 1,
    "field1": "value1",
    "field2": "value2"
}
```

### Error Response
```json
{
    "error": "Error message"
}
```

### Paginated Response
```json
{
    "count": 100,
    "next": "http://localhost:8000/api/endpoint/?page=2",
    "previous": null,
    "results": [...]
}
```

## HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Permission denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Authentication

Most endpoints require authentication. Include the user's session cookie or use token authentication for mobile apps.

## Rate Limiting

API requests are limited to 1000 requests per hour per user.

## CORS

CORS is enabled for the following origins:
- http://localhost:3000
- http://127.0.0.1:3000
- http://localhost:8080
- http://127.0.0.1:8080

## File Uploads

For file uploads (profile pictures, project submissions), use multipart/form-data encoding.

## Examples

### Flutter/Dart Example
```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

class ApiService {
  static const String baseUrl = 'http://localhost:8000/api';
  
  Future<Map<String, dynamic>> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login/'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'username': username,
        'password': password,
      }),
    );
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to login');
    }
  }
  
  Future<List<dynamic>> getStudentLessons(String studentId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/students/$studentId/lessons/'),
    );
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to load lessons');
    }
  }
}
```

### JavaScript/React Example
```javascript
const API_BASE_URL = 'http://localhost:8000/api';

export const apiService = {
  async login(username, password) {
    const response = await fetch(`${API_BASE_URL}/auth/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });
    
    if (!response.ok) {
      throw new Error('Login failed');
    }
    
    return response.json();
  },
  
  async getStudentLessons(studentId) {
    const response = await fetch(`${API_BASE_URL}/students/${studentId}/lessons/`);
    
    if (!response.ok) {
      throw new Error('Failed to load lessons');
    }
    
    return response.json();
  },
};
``` 