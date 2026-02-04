# GradeIt - AI-Powered Assignment Grading System

## Overview

GradeIt is a CLI application that helps teachers grade student Java assignments. It uses AI to help grade assignments and provide feedback to students. It will also provide a way for teachers to track student progress and provide feedback to students.

## Core Features

### User Input
- Provide assignment name
- Provide where to put the assignment (working directory)
- Provide where the solution is located

### Gather Data
- Use `students.txt` file to get student group names
- Using the student group name, create a folder for each student
- Clone the repository for each student from GitLab

### Grading
- Each assignment is using Gradle to build the assignment
- Ensure the assignment builds successfully and if there are tests, ensure they pass
- Ensure code is following Java conventions and best practices
- Compare the student's code to the solution code
- Use AI to grade the assignment
- Provide feedback to the student
- Provide a grade to the student

### Feedback
- Create a single file containing feedback for all students

## Technical Requirements

### Interface
- **Type**: Command-line interface (CLI)
- **Language**: Python (recommended for AI integration and scripting)

### GitLab Integration
- **Authentication**: SSH (assumes SSH keys are already configured)
- **Repository URL Format**: `git@gitlab.hfcc.edu:<student-group>/<assignment-name>.git`
  - Example: `git@gitlab.hfcc.edu:mawall-2026-winter-cis-271-01/fizzbuzz.git`
- **Student Group Format**: `<username>-<semester>-<course>-<section>`
  - Example: `mawall-2026-winter-cis-271-01`

### AI Integration
- **Provider**: Anthropic/Claude
- **API Key**: Required (via environment variable or config file)
- **Use Cases**: 
  - Code quality analysis
  - Comparison with solution code
  - Feedback generation
  - Grading assistance

### Input Files
- **students.txt**: Plain text file with one student group name per line
  - Format: Full group names (e.g., `mawall-2026-winter-cis-271-01`)
- **Solution Code**: Directory path to reference solution

### Build System
- **Tool**: Gradle
- **Requirements**: 
  - Must build successfully
  - Must pass all tests (if present)

### Output
- **Format**: Single file containing all students' feedback
- **File Type**: Markdown (for readability and formatting)
- **Contents**: 
  - Student name/group
  - Build status
  - Test results
  - Code quality assessment
  - AI-generated feedback
  - Grade

## Success Criteria

- Successfully clone all student repositories from GitLab
- Build each assignment with Gradle
- Run tests and capture results
- Generate meaningful AI-powered feedback
- Produce a comprehensive feedback report for all students
- Handle errors gracefully (missing repos, build failures, etc.)

## Out of Scope (for initial version)

- Web interface
- Database storage
- Student authentication/login
- Real-time grading
- Integration with LMS (Learning Management Systems)