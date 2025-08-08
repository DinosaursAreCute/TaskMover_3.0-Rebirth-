# Programming Courses Resource

## Overview

The TaskMover application now includes a dedicated **Programming Courses** tab that provides users with access to curated, high-quality interactive programming courses that are available for free.

## Purpose

This feature addresses the common need for finding reliable, free programming education resources. Instead of searching through countless websites and potentially low-quality content, users can access a carefully selected collection of proven educational platforms.

## Features

### 🎓 Curated Course Collection
- **6 high-quality platforms** selected for their interactive approach and proven track record
- Courses cover multiple programming languages and skill levels
- All resources are completely free to access

### 🔍 Search & Filter Functionality
- **Search bar**: Find courses by name, provider, or programming language
- **Level filter**: Filter by skill level (Beginner, Intermediate, Advanced)
- **Real-time filtering**: Results update instantly as you type

### 📚 Course Information Display
- Detailed course descriptions and features
- Programming languages covered
- Skill level requirements
- Key features highlighted for each platform

### 🌐 Direct Access
- **One-click access**: Visit any course directly in your web browser
- **Double-click shortcuts**: Quick access to course websites
- Integrated web browser opening

## Included Courses

### 1. freeCodeCamp
- **Provider**: freeCodeCamp.org
- **Languages**: JavaScript, Python, HTML/CSS, React, Node.js
- **Level**: Beginner to Advanced
- **Features**: Interactive challenges, Real projects, Free certificates, Community forum

### 2. Codecademy Free Courses
- **Provider**: Codecademy
- **Languages**: Python, JavaScript, HTML/CSS, Java, C++
- **Level**: Beginner to Intermediate
- **Features**: Interactive exercises, Immediate feedback, Progress tracking, Code editor

### 3. Khan Academy Programming
- **Provider**: Khan Academy
- **Languages**: JavaScript, HTML/CSS, SQL
- **Level**: Beginner
- **Features**: Visual programming, Creative projects, Step-by-step tutorials, Community showcase

### 4. The Odin Project
- **Provider**: The Odin Project
- **Languages**: JavaScript, Ruby, HTML/CSS, Git
- **Level**: Beginner to Intermediate
- **Features**: Project-based learning, Open source, Community support, Real applications

### 5. SoloLearn
- **Provider**: SoloLearn
- **Languages**: Python, Java, C++, JavaScript, PHP
- **Level**: Beginner to Intermediate
- **Features**: Mobile app, Code challenges, Community, Progress tracking

### 6. CS50x - Introduction to Computer Science
- **Provider**: Harvard University (edX)
- **Languages**: C, Python, SQL, JavaScript, HTML/CSS
- **Level**: Beginner to Intermediate
- **Features**: University-level content, Problem sets, Video lectures, Online IDE

## How to Use

1. **Access the Feature**: Click on the "📚 Courses" tab in the TaskMover application
2. **Browse Courses**: View the complete list of available courses
3. **Search/Filter**: Use the search box or level filter to find specific courses
4. **View Details**: Click on any course to see detailed information
5. **Visit Course**: Click "🌐 Visit Course" or double-click a course to open it in your browser

## Technical Implementation

### Architecture
- Built using TaskMover's existing UI component system
- Follows the established design patterns and theme system
- Integrated seamlessly with the main application tabs

### Data Structure
```python
class CourseData:
    title: str          # Course name
    provider: str       # Organization providing the course
    url: str           # Direct link to the course
    description: str   # Detailed description
    language: str      # Programming languages covered
    level: str         # Skill level required
    features: List[str] # Key features and benefits
```

### Component Features
- **Responsive design**: Works with TaskMover's theme system
- **Accessibility**: Keyboard navigation and screen reader support
- **Error handling**: Graceful handling of web browser opening failures
- **Logging**: All interactions are logged for debugging

## Benefits for TaskMover Users

### Educational Enhancement
- Helps users improve their programming skills
- Provides structured learning paths
- Access to high-quality, free education

### Time Saving
- No need to research and evaluate countless course options
- Curated selection removes low-quality resources
- Quick access to proven educational platforms

### Skill Development
- Covers multiple programming languages
- Various skill levels accommodated
- Interactive learning approach emphasized

## Future Enhancements

Potential improvements for future versions:

1. **Course Progress Tracking**: Integration with course platforms to track progress
2. **Personal Recommendations**: AI-based course suggestions based on user interests
3. **Community Features**: User reviews and ratings for courses
4. **Learning Paths**: Suggested sequences of courses for specific goals
5. **Local Content**: Offline course materials and exercises

## Maintenance

### Adding New Courses
To add new courses to the collection:

1. Update the `COURSES_DATA` list in `programming_courses_component.py`
2. Follow the existing `CourseData` structure
3. Ensure the course meets quality criteria:
   - Interactive learning approach
   - Free access
   - Proven educational value
   - Active community or support

### Quality Criteria
Courses are selected based on:
- **Free Access**: Must be available at no cost
- **Interactive Elements**: Hands-on coding, not just videos
- **Community**: Active support community or forums
- **Track Record**: Proven success in teaching programming
- **Modern Content**: Up-to-date with current best practices

This feature transforms TaskMover from just a file organization tool into a more comprehensive productivity platform that supports users' professional development and learning goals.