# Financial Statement Analyzer

Multi-User Bank Statement Processing & Analysis System

## Features

- 📄 PDF Bank Statement Parsing (HSBC, AMEX, NatWest, Barclays)
- 🔄 Transaction Matching Across Multiple Statements
- 📊 Financial Categorization (Asset, Liability, Equity, Income, Expense)
- ✅ Balance Validation & Reconciliation
- 📈 Interactive Visualizations
- 📤 Multiple Export Formats (CSV, Excel, PDF, JSON)
- 🔍 Advanced Filtering & Search
- 👥 Multi-User Support with Authentication

## Project Structure

```
├── backend/          # FastAPI backend
├── frontend/         # React/TypeScript frontend
├── tests/           # Test files
└── docs/            # Documentation
```

## Getting Started

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Note**: The project uses a working bank statement parser from GitHub. The package will be automatically installed from `https://github.com/dalemarana/bankStatementParser.git` when you run `pip install -r requirements.txt`.

If you encounter issues with the GitHub parser installation, you can install it manually:
```bash
pip install git+https://github.com/dalemarana/bankStatementParser.git@main
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

## Development

See `IMPLEMENTATION_PLAN.md` for detailed implementation plan.

## GitHub Parser Integration

This project integrates the working bank statement parser from the GitHub repository. See `GITHUB_INTEGRATION_PLAN.md` for the comprehensive integration plan and `INTEGRATION_SUMMARY.md` for a summary of what was implemented.

### Key Features
- ✅ Uses working GitHub parser as primary parser
- ✅ Automatic fallback to new parser if GitHub parser fails
- ✅ Seamless integration with existing FastAPI structure
- ✅ Comprehensive test coverage

### Configuration

The GitHub parser is enabled by default. You can configure it in `backend/src/config.py` or via environment variables:

```env
USE_GITHUB_PARSER=true
GITHUB_PARSER_FALLBACK=true
```

## Git Commands

### Initial Setup (First Time)

```bash
# Initialize Git repository (if not already initialized)
git init

# Add remote repository
git remote add origin https://github.com/dalemarana/Cursor-Financial-Statement-Analyzer.git

# Add all files to staging
git add .

# Create initial commit
git commit -m "Initial commit: Financial Statement Analyzer with multi-user support, PDF parsing, and transaction matching"

# Push to GitHub (first time)
git push -u origin main
```

### Regular Workflow

```bash
# Check status of changes
git status

# Add specific files or all changes
git add .                    # Add all changes
git add <file>               # Add specific file

# Commit changes with descriptive message
git commit -m "Description of changes made"

# Push to GitHub
git push origin main         # Push to main branch
git push origin <branch>     # Push to specific branch
```

### Branch Management

```bash
# Create and switch to new branch
git checkout -b feature/new-feature

# Switch branches
git checkout main
git checkout <branch-name>

# Push new branch to remote
git push -u origin feature/new-feature
```

### Useful Commands

```bash
# View commit history
git log

# View changes in files
git diff

# Pull latest changes from remote
git pull origin main

# Clone repository (for other developers)
git clone https://github.com/dalemarana/Cursor-Financial-Statement-Analyzer.git
```

## License

MIT

