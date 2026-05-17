#!/usr/bin/env python3
"""
Research Agent Chatbot - Git Reorganization Script v4.0 (FIXED)
Handles uncommitted changes properly before reorganization
"""

import subprocess
import sys
import os
from pathlib import Path

class ChatbotReorganizer:
    """Reorganize git repository for v4.0.0 release."""
    
    def __init__(self):
        self.version = "4.0.0"
        
        # Define feature branches with their commits
        self.features = {
            "foundation": {
                "branch": "feature/01-foundation",
                "description": "Core infrastructure: config, logging, errors",
                "commits": ["ae697e2", "8d83756", "53081c0"],
                "new_files": ["src/__init__.py", "requirements.txt"],
                "base": None
            },
            "data-layer": {
                "branch": "feature/02-data-layer",
                "description": "Data abstraction: mock data + data sources",
                "commits": ["798b87b", "0717d55"],
                "new_files": [],
                "base": "feature/01-foundation"
            },
            "state-management": {
                "branch": "feature/03-state-management",
                "description": "State management and base agent structure",
                "commits": ["cf92429", "d515a52"],
                "new_files": [],
                "base": "feature/02-data-layer"
            },
            "orchestration": {
                "branch": "feature/04-orchestration",
                "description": "LangGraph orchestration framework",
                "commits": ["2abe080"],
                "new_files": [],
                "base": "feature/03-state-management"
            },
            "research-agent": {
                "branch": "feature/05-research-agent",
                "description": "Research Agent: data gathering and aggregation",
                "commits": ["2e3e016"],
                "new_files": [],
                "base": "feature/04-orchestration"
            },
            "validator-agent": {
                "branch": "feature/06-validator-agent",
                "description": "Validator Agent: quality control with retry logic",
                "commits": ["1fef13e"],
                "new_files": [],
                "base": "feature/05-research-agent"
            },
            "synthesis-agent": {
                "branch": "feature/07-synthesis-agent",
                "description": "Synthesis Agent: response formatting",
                "commits": ["a96f7c6"],
                "new_files": [],
                "base": "feature/06-validator-agent"
            },
            "complete-pipeline": {
                "branch": "feature/08-complete-pipeline",
                "description": "Complete agent pipeline with conditional routing",
                "commits": ["314ae72"],
                "new_files": [],
                "base": "feature/07-synthesis-agent"
            },
            "integration-testing": {
                "branch": "feature/09-integration-testing",
                "description": "Production testing with Groq LLM integration",
                "commits": ["6b1298a"],
                "new_files": [],
                "base": "feature/08-complete-pipeline"
            },
            "deployment": {
                "branch": "feature/10-deployment",
                "description": "Deployment configuration and packaging",
                "commits": [],
                "new_files": ["setup.py"],
                "base": "feature/09-integration-testing"
            }
        }
    
    def run(self, cmd: str, check=True, silent=False) -> subprocess.CompletedProcess:
        """Run shell command."""
        if not silent:
            print(f"  → {cmd}")
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0 and check:
            print(f"    ❌ Error: {result.stderr}")
            if check:
                sys.exit(1)
        if result.stdout.strip() and not silent:
            print(f"    {result.stdout.strip()}")
        return result
    
    def update_gitignore(self):
        """Update .gitignore to exclude personal prep files."""
        print("\n📝 STEP 1: Update .gitignore")
        print("=" * 70)
        
        gitignore_path = Path(".gitignore")
        
        # Read current content
        if gitignore_path.exists():
            current = gitignore_path.read_text()
        else:
            current = ""
        
        # Add personal prep files section
        additions = """
# Personal preparation and notes (not for public repo)
Interview Question Bank.MD
**/interview_*.md
**/notes_*.txt
"""
        
        if "Interview Question Bank.MD" not in current:
            with open(gitignore_path, 'a') as f:
                f.write(additions)
            print("✅ Added personal files to .gitignore")
        else:
            print("✅ .gitignore already configured")
    
    def handle_uncommitted_changes(self):
        """Handle uncommitted changes before reorganization."""
        print("\n🔍 STEP 2: Check for Uncommitted Changes")
        print("=" * 70)
        
        # Check for any changes (staged, modified, untracked)
        status = self.run("git status --porcelain", silent=True).stdout.strip()
        
        if not status:
            print("✅ Working directory is clean")
            return []
        
        print("\n⚠️  Found uncommitted changes:")
        print(status)
        
        # Separate different types of changes
        staged = []
        modified = []
        untracked = []
        
        for line in status.split('\n'):
            if not line.strip():
                continue
            
            status_code = line[:2]
            filename = line[3:].strip()
            
            # Skip Interview Question Bank
            if "Interview Question Bank" in filename:
                print(f"\n⏭️  Skipping (personal file): {filename}")
                continue
            
            if status_code[0] in ['A', 'M', 'D']:
                staged.append(filename)
            elif status_code[1] in ['M', 'D']:
                modified.append(filename)
            elif status_code == '??':
                untracked.append(filename)
        
        # Show what we found
        all_files = staged + modified + untracked
        if all_files:
            print(f"\n📋 Files to handle:")
            for f in all_files:
                print(f"   - {f}")
        
        # Ask user what to do
        print("\n🤔 How to handle these changes?")
        print("   1. Commit them now (recommended)")
        print("   2. Stash them (can restore later)")
        print("   3. Discard them (⚠️  LOSES CHANGES)")
        
        choice = input("\nChoose option (1/2/3): ").strip()
        
        if choice == "1":
            print("\n📝 Committing changes...")
            # Stage everything except Interview Question Bank
            for f in all_files:
                self.run(f'git add "{f}"', check=False)
            
            self.run('git commit -m "chore: commit changes before v4.0 reorganization"')
            print("✅ Changes committed")
            
        elif choice == "2":
            print("\n📦 Stashing changes...")
            self.run('git stash push -u -m "Before v4.0 reorganization"')
            print("✅ Changes stashed")
            print("   To restore later: git stash pop")
            
        elif choice == "3":
            confirm = input("\n⚠️  Are you SURE you want to discard changes? (type 'yes'): ")
            if confirm.lower() == "yes":
                print("\n🗑️  Discarding changes...")
                self.run("git reset --hard HEAD")
                self.run("git clean -fd")
                print("✅ Changes discarded")
            else:
                print("❌ Cancelled. Please run script again.")
                sys.exit(0)
        else:
            print("❌ Invalid choice. Exiting.")
            sys.exit(0)
        
        return all_files
    
    def create_backup(self):
        """Create backup of current state."""
        print("\n💾 STEP 3: Create Backup")
        print("=" * 70)
        
        # Create backup branch
        self.run("git branch -f master-backup-v3 master")
        print("✅ Created backup: master-backup-v3")
        
        # Also tag current state
        self.run("git tag -f v3.0.0-archive master", check=False)
        print("✅ Tagged current state: v3.0.0-archive")
        
        print("\n   Recovery commands if needed:")
        print("   → git reset --hard master-backup-v3")
        print("   → git checkout v3.0.0-archive")
    
    def create_feature_branches(self):
        """Create all feature branches."""
        print("\n🌳 STEP 4: Create Feature Branches")
        print("=" * 70)
        
        for key, feature in self.features.items():
            print(f"\n{'='*70}")
            print(f"📌 {feature['branch']}")
            print(f"   {feature['description']}")
            print(f"{'='*70}")
            
            # Determine starting point
            if feature['base'] is None:
                # Start from first commit (gitignore)
                self.run(f"git checkout -b {feature['branch']} b9a4b7f")
            else:
                # Branch from previous feature
                base_branch = self.features[feature['base'].split('/')[-1]]['branch']
                self.run(f"git checkout {base_branch}")
                self.run(f"git checkout -b {feature['branch']}")
            
            # Cherry-pick commits
            if feature['commits']:
                for commit in feature['commits']:
                    print(f"   📥 Cherry-picking {commit}...")
                    result = self.run(f"git cherry-pick {commit}", check=False, silent=True)
                    if result.returncode != 0:
                        if "already exists" in result.stderr or "empty" in result.stderr:
                            print(f"      ℹ️  Already applied, skipping")
                            self.run("git cherry-pick --abort", check=False, silent=True)
                        else:
                            print(f"      ⚠️  Conflict detected")
                            print(f"      {result.stderr}")
                            return False
            
            # Add new files for this feature
            if feature['new_files']:
                files_added = []
                for file in feature['new_files']:
                    if Path(file).exists():
                        self.run(f'git add "{file}"', check=False)
                        files_added.append(file)
                
                if files_added:
                    commit_msg = f"feat: add {', '.join([f.split('/')[-1] for f in files_added])}"
                    result = self.run(f'git commit -m "{commit_msg}"', check=False)
                    if result.returncode == 0:
                        print(f"   ✅ Added: {', '.join(files_added)}")
                    else:
                        print(f"   ℹ️  Files already in previous commits")
            
            # Show summary
            commit_count = len(feature['commits']) + (1 if feature['new_files'] and Path(feature['new_files'][0]).exists() else 0)
            print(f"\n   ✅ Branch created with {commit_count} commit(s)")
        
        return True
    
    def create_main_v4(self):
        """Create clean main branch for v4.0."""
        print("\n🎯 STEP 5: Create v4.0.0 Release")
        print("=" * 70)
        
        # Switch to master
        self.run("git checkout master")
        
        # Merge final feature branch (if needed)
        print("\n   Checking if merge needed...")
        result = self.run("git rev-list master..feature/10-deployment --count", silent=True)
        commits_ahead = int(result.stdout.strip()) if result.stdout.strip() else 0
        
        if commits_ahead > 0:
            print(f"   → Merging {commits_ahead} new commit(s) from feature/10-deployment")
            self.run('git merge feature/10-deployment -m "release: merge all features for v4.0.0"')
        else:
            print("   ℹ️  Master already up to date")
        
        # Tag v4.0.0
        tag_message = "v4.0.0 - Production Ready Release\\n\\nFeatures:\\n- Complete 4-agent pipeline\\n- LangGraph orchestration\\n- Groq integration\\n- Production deployment ready"
        
        self.run(f'git tag -a v{self.version} -m "{tag_message}"')
        print(f"\n✅ Tagged release: v{self.version}")
    
    def create_readme_updates(self):
        """Create updated README badges and structure."""
        print("\n📚 STEP 6: Update Documentation")
        print("=" * 70)
        
        readme_badges = """<!-- Add these badges to your README.md -->

![Version](https://img.shields.io/badge/version-4.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![LangGraph](https://img.shields.io/badge/LangGraph-enabled-orange)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen)

## 🏗️ Architecture

```
User Query → Clarity Agent → Research Agent → Validator → Synthesis → Response
                                                  ↑            ↓
                                                  └─ Retry ───┘
```

## 📂 Feature Branches

- `feature/01-foundation` - Core infrastructure
- `feature/02-data-layer` - Data abstraction
- `feature/03-state-management` - State & agents
- `feature/04-orchestration` - LangGraph setup
- `feature/05-research-agent` - Research Agent
- `feature/06-validator-agent` - Validator Agent
- `feature/07-synthesis-agent` - Synthesis Agent
- `feature/08-complete-pipeline` - Full pipeline
- `feature/09-integration-testing` - Production tests
- `feature/10-deployment` - Deployment config
"""
        
        Path("README_BADGES.md").write_text(readme_badges)
        print("✅ Created README_BADGES.md")
    
    def show_summary(self):
        """Show final summary."""
        print("\n" + "=" * 70)
        print("✅ REORGANIZATION COMPLETE - v4.0.0")
        print("=" * 70)
        
        print("\n📊 Created Branches:")
        result = self.run("git branch", silent=True)
        for line in result.stdout.split('\n'):
            if line.strip() and 'feature/' in line:
                print(f"   {line.strip()}")
        
        print("\n🏷️  Version Tags:")
        print(f"   v{self.version} (current)")
        print("   v3.0.0-archive (backup)")
        
        print("\n🚀 Next Steps:")
        print("\n1️⃣  Push to GitHub:")
        print("   git remote add origin https://github.com/yourusername/research-agent")
        print("   git push -u origin master")
        print("   git push --all origin")
        print("   git push --tags")
        
        print("\n2️⃣  Update README:")
        print("   cat README_BADGES.md")
        
        print("\n3️⃣  View structure:")
        print("   git log --all --graph --oneline --decorate")
        
        print("\n🛡️  Safety: master-backup-v3 (restore with: git reset --hard master-backup-v3)")

def main():
    """Run the reorganization."""
    
    print("=" * 70)
    print("🚀 RESEARCH AGENT CHATBOT - v4.0.0 REORGANIZATION (FIXED)")
    print("=" * 70)
    print("\nThis script will:")
    print("  ✅ Handle uncommitted changes properly")
    print("  ✅ Create 10 feature branches")
    print("  ✅ Add setup files to appropriate branches")
    print("  ✅ Ignore Interview Question Bank.MD")
    print("  ✅ Tag release as v4.0.0")
    print("  ✅ Create backup (master-backup-v3)")
    
    confirm = input("\n🤔 Ready to proceed? (yes/no): ")
    if confirm.lower() not in ["yes", "y"]:
        print("\n❌ Cancelled.")
        return 0
    
    organizer = ChatbotReorganizer()
    
    try:
        # Update gitignore first
        organizer.update_gitignore()
        
        # Handle uncommitted changes (FIXED!)
        organizer.handle_uncommitted_changes()
        
        # Create backup
        organizer.create_backup()
        
        # Create feature branches
        success = organizer.create_feature_branches()
        if not success:
            print("\n❌ Failed to create branches. Restoring backup...")
            subprocess.run("git checkout master", shell=True)
            subprocess.run("git reset --hard master-backup-v3", shell=True)
            return 1
        
        # Create v4.0 release
        organizer.create_main_v4()
        
        # Update docs
        organizer.create_readme_updates()
        
        # Show summary
        organizer.show_summary()
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Repository ready for v4.0.0")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted! Restoring from backup...")
        subprocess.run("git checkout master", shell=True)
        subprocess.run("git reset --hard master-backup-v3", shell=True)
        print("✅ Restored to original state")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n🔧 To restore:")
        print("   git checkout master")
        print("   git reset --hard master-backup-v3")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())