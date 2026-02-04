# GradeIt - AI-Powered Assignment Grading System

An automated grading system for Java assignments hosted on GitLab, using AI to provide intelligent feedback and grading.

## Features

- 🤖 AI-powered code analysis using Anthropic/Claude
- 📦 Automated repository cloning from GitLab (SSH)
- 🔨 Gradle build and test execution
- 📊 Comprehensive feedback reports
- ⚙️ Flexible configuration system

## Setup

### Prerequisites

- Python 3.12+
- Git with SSH access to GitLab
- Gradle (for building student assignments)

### Installation

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

3. Activate the virtual environment:
   ```bash
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate  # Windows
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Configure `config.properties`:
   - Set your `base_directory`
   - Set your `current_semester_directory`
   - Add your Anthropic API key to `anthropic_api_key`

## Usage

```bash
./venv/bin/python gradeit.py \
  --assignment <assignment-name> \
  --solution <path-to-solution> \
  [--config config.properties] \
  [--max-grade 100] \
  [--passing-grade 60]
```

### Example

```bash
./venv/bin/python gradeit.py \
  --assignment fizzbuzz \
  --solution /path/to/solution/fizzbuzz
```

## Configuration

Edit `config.properties` to customize:

- **base_directory**: Base path for all project files
- **current_semester_directory**: Current semester folder name
- **students_file**: Path to students.txt (list of student GitLab groups)
- **gitlab_host**: GitLab server hostname
- **output_directory**: Where to save feedback reports
- **anthropic_api_key**: Your Claude API key

## Project Structure

```
GradeIt/
├── src/
│   └── gradeit/
│       ├── __init__.py
│       ├── cli.py              # Command-line interface
│       └── config_loader.py    # Configuration parser
├── config.properties           # Configuration file
├── requirements.txt            # Python dependencies
├── gradeit.py                  # Main entry point
└── README.md
```

## Development Status

✅ Project setup complete
🚧 Core functionality in progress
⏳ AI integration pending
⏳ Output generation pending

## License

Educational use only.
