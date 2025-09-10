# BuzzAtt Frontend Integration Guide

## Base URL
```
http://localhost:8001
```

## Authentication

### 1. Register a New User

**Endpoint:** `POST /auth/register`

**Request Body:**
```javascript
// For Students
{
    "email": "student@example.com",
    "first_name": "Jane",
    "last_name": "Smith",
    "matric_number": "FUO/20/CSI/1334",  // Required for students
    "department": "Computer Science",
    "faculty": "Engineering",
    "password": "yourpassword",
    "profile_type": "student"
}

// For Lecturers
{
    "email": "lecturer@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "department": "Computer Science",
    "faculty": "Engineering",
    "password": "yourpassword",
    "profile_type": "lecturer"
}
```

**Response (200):**
```javascript
{
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "department": "Computer Science",
    "faculty": "Engineering",
    "matric_number": "FUO/20/CSI/1334"  // Only for students
}
```

### 2. Login

**Endpoint:** `POST /auth/login`

**Request Body (form-data):**
```javascript
{
    "username": "user@example.com",  // Use email as username
    "password": "yourpassword"
}
```

**Response (200):**
```javascript
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "matric_number": "FUO/20/CSI/1334",  // null for lecturers
    "email": "user@example.com",
    "profile_type": "student"  // or "lecturer"
}
```

**Using the Token:**
Add the token to all subsequent requests in the Authorization header:
```javascript
headers: {
    'Authorization': 'Bearer <access_token>'
}
```

## Attendance Management (Lecturer Only)

### 1. Save Session Attendance

**Endpoint:** `POST /lecturer/attendance/save-session`

**Request Body:**
```javascript
{
    "session_id": "CSC101_2025_09_10",  // Unique session identifier
    "course_name": "CSC101",
    "session_start": "2025-09-10T09:00:00Z",  // ISO timestamp
    "session_end": "2025-09-10T11:00:00Z",    // ISO timestamp
    "session_duration": 7200,  // Duration in seconds
    "students": [
        {
            "matric_number": "FUO/20/CSI/1334",
            "timestamp": "2025-09-10T09:05:00Z",
            "ip_address": "192.168.1.100"
        }
        // ... more students
    ]
}
```

**Response (200):**
```javascript
{
    "success": true,
    "message": "Session attendance saved successfully",
    "saved_count": 1  // Number of students saved
}
```

### 2. Get Sessions History

**Endpoint:** `GET /lecturer/attendance/sessions`

**Query Parameters (all optional):**
- course_name: string
- from_date: ISO date (YYYY-MM-DD)
- to_date: ISO date (YYYY-MM-DD)

**Example:**
```
GET /lecturer/attendance/sessions?course_name=CSC101&from_date=2025-09-01&to_date=2025-09-30
```

**Response (200):**
```javascript
{
    "sessions": [
        {
            "session_id": "CSC101_2025_09_10",
            "course_name": "CSC101",
            "date": "2025-09-10",
            "start_time": "2025-09-10T09:00:00Z",
            "end_time": "2025-09-10T11:00:00Z",
            "duration": 7200,
            "total_students": 1,
            "students": [
                {
                    "matric_number": "FUO/20/CSI/1334",
                    "timestamp": "2025-09-10T09:05:00Z",
                    "ip_address": "192.168.1.100"
                }
                // ... more students
            ]
        }
        // ... more sessions
    ],
    "total_sessions": 1
}
```

## Frontend Implementation Tips

1. **State Management:**
   - Store the access token securely (e.g., in localStorage or secure cookie)
   - Store user profile type to show/hide lecturer-specific features
   - Store matric number for students

2. **Authentication Flow:**
```javascript
// Example using fetch API
async function login(email, password) {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch('http://localhost:8001/auth/login', {
        method: 'POST',
        body: formData
    });

    if (response.ok) {
        const data = await response.json();
        // Store token and user info
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('userProfile', JSON.stringify({
            email: data.email,
            profileType: data.profile_type,
            matricNumber: data.matric_number
        }));
        return data;
    }
    throw new Error('Login failed');
}
```

3. **Protected API Calls:**
```javascript
async function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };

    const response = await fetch(url, {
        ...options,
        headers
    });

    if (response.status === 401) {
        // Token expired or invalid
        // Redirect to login
        window.location.href = '/login';
        return;
    }

    return response;
}

// Example usage
async function getSessions(courseCode, fromDate, toDate) {
    const params = new URLSearchParams();
    if (courseCode) params.append('course_name', courseCode);
    if (fromDate) params.append('from_date', fromDate);
    if (toDate) params.append('to_date', toDate);

    const response = await fetchWithAuth(
        `http://localhost:8001/lecturer/attendance/sessions?${params}`
    );
    return response.json();
}
```

4. **Error Handling:**
```javascript
async function makeApiCall(endpoint, options) {
    try {
        const response = await fetchWithAuth(endpoint, options);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API call failed');
        }
        return await response.json();
    } catch (error) {
        // Handle error appropriately
        console.error('API Error:', error);
        throw error;
    }
}
```

5. **Route Protection:**
```javascript
function requireLecturer(Component) {
    return function ProtectedRoute(props) {
        const userProfile = JSON.parse(localStorage.getItem('userProfile') || '{}');
        
        if (!userProfile.profileType || userProfile.profileType !== 'lecturer') {
            // Redirect to login or unauthorized page
            return <Redirect to="/unauthorized" />;
        }
        
        return <Component {...props} />;
    }
}

// Usage in routes
const AttendanceManagement = requireLecturer(AttendanceManagementComponent);
```

## Common HTTP Status Codes

- 200: Success
- 400: Bad Request (invalid input)
- 401: Unauthorized (invalid/missing token)
- 403: Forbidden (insufficient permissions)
- 404: Not Found
- 500: Internal Server Error

## Data Validation

1. **Email**: Must be a valid email format
2. **Matric Number**: Required for students
3. **Passwords**: Sent as plain text, hashed on server
4. **Dates**: ISO format (YYYY-MM-DDTHH:mm:ssZ)

## Mobile App Integration (React Native)

### Connecting to localhost from physical device

1. **Find your computer's local IP address:**
```bash
# On Linux/Mac
ip addr show

# Or
ifconfig

# On Windows
ipconfig
```
Look for your local network IP (usually starts with 192.168.x.x or 10.0.x.x)

2. **Update the Base URL in your React Native app:**
```javascript
// Instead of http://localhost:8001
const BASE_URL = 'http://192.168.1.xxx:8001';  // Replace with your computer's IP
```

3. **Allow all network connections in development:**
Update uvicorn command to listen on all interfaces:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

4. **Android-specific setup:**
Add this to your Android manifest (`android/app/src/main/AndroidManifest.xml`):
```xml
<application
    ...
    android:usesCleartextTraffic="true">
```

5. **iOS-specific setup:**
Add this to your `Info.plist`:
```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>
```

### Example React Native API Client
```javascript
// api.js
const API_URL = __DEV__ 
  ? 'http://192.168.1.xxx:8001'  // Development (replace with your IP)
  : 'https://your-production-api.com';  // Production

export const api = {
  login: async (email, password) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    return data;
  },

  // Example of a protected API call
  getSessions: async (token) => {
    const response = await fetch(`${API_URL}/lecturer/attendance/sessions`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch sessions');
    }

    return response.json();
  },
};

// Usage in your React Native components
import { api } from './api';
import AsyncStorage from '@react-native-async-storage/async-storage';

const LoginScreen = () => {
  const handleLogin = async () => {
    try {
      const result = await api.login(email, password);
      // Store token securely
      await AsyncStorage.setItem('token', result.access_token);
      await AsyncStorage.setItem('userProfile', JSON.stringify({
        email: result.email,
        profileType: result.profile_type,
        matricNumber: result.matric_number
      }));
      // Navigate to main app
    } catch (error) {
      // Handle error
    }
  };
};
```

## Security Considerations

1. Always use HTTPS in production
2. Store tokens securely using AsyncStorage or a more secure alternative like EncryptedStorage
3. Implement token refresh mechanism for longer sessions
4. Validate all user inputs
5. Implement proper logout by clearing stored tokens
6. Never commit API URLs or sensitive configurations
