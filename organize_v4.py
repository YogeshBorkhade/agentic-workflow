#!/usr/bin/env python3
"""
Research Agent Chatbot - Individual Feature Branches v4.0
Creates SEPARATE branches for each feature (not cumulative)

Each branch shows ONLY that feature's work:
- feature/foundation → ONLY foundation commits
- feature/research-agent → ONLY research agent commit
- feature/validator-agent → ONLY validator commit
etc.
"""

import subprocess
import sys
from pathlib import Path

class IndividualFeatureBranches:
    """Create separate, isolated branches for each feature."""
    
    def __init__(self):
        self.version = "4.0.0"
        
        # Define individual features (NOT cumulative)
        self.features = [
            {
                "name": "foundation",
                "branch": "feature/foundation",
                "description": "Core infrastructure: config, logging, error handling",
                "commits": ["ae697e2", "8d83756", "53081c0"],
                "base_commit": "b9a4b7f",  # Start from .gitignore
                "files": ["src/__init__.py", "requirements.txt"]
            },
            {
                "name": "data-layer",
                "branch": "feature/data-layer",
                "description": "Data abstraction and mock data system",
                "commits": ["798b87b", "0717d55"],
                "base_commit": "53081c0",  # After foundation
                "files": []
            },
            {
                "name": "clarity-agent",
                "branch": "feature/clarity-agent",
                "description": "ClarityAgent: intent and company extraction",
                "commits": ["cf92429", "d515a52"],
                "base_commit": "0717d55",  # After data layer
                "files": []
            },
            {
                "name": "orchestration",
                "branch": "feature/orchestration",
                "description": "LangGraph orchestration framework",
                "commits": ["2abe080"],
                "base_commit": "d515a52",  # After clarity agent
                "files": []
            },
            {
                "name": "research-agent",
                "branch": "feature/research-agent",
                "description": "ResearchAgent: data gathering and aggregation",
                "commits": ["2e3e016"],
                "base_commit": "2abe080",  # After orchestration
                "files": []
            },
            {
                "name": "validator-agent",
                "branch": "feature/validator-agent",
                "description": "ValidatorAgent: quality control with retry logic",
                "commits": ["1fef13e"],
                "base_commit": "2e3e016",  # After research agent
                "files": []
            },
            {
                "name": "synthesis-agent",
                "branch": "feature/synthesis-agent",
                "description": "SynthesisAgent: response formatting and structuring",
                "commits": ["a96f7c6"],
                "base_commit": "1fef13e",  # After validator
                "files": []
            },
            {
                "name": "pipeline-integration",
                "branch": "feature/pipeline-integration",
                "description": "Complete pipeline: wire all agents with routing",
                "commits": ["314ae72"],
                "base_commit": "a96f7c6",  # After synthesis
                "files": []
            },
            {
                "name": "groq-integration",
                "branch": "feature/groq-integration",
                "description": "Production testing with Groq LLM",
                "commits": ["6b1298a"],
                "base_commit": "314ae72",  # After pipeline
                "files": []
            },
            {
                "name": "deployment",
                "branch": "feature/deployment",
                "description": "Deployment configuration and packaging",
                "commits": [],
                "base_commit": "6b1298a",  # After groq
                "files": ["setup.py"]
            }
        ]
    
    def run(self, cmd: str, check=True, silent=False):
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
        """Update .gitignore."""
        print("\n📝 STEP 1: Update .gitignore")
        print("=" * 70)
        
        gitignore_path = Path(".gitignore")
        current = gitignore_path.read_text() if gitignore_path.exists() else ""
        
        additions = """
# Personal preparation and notes
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
        """Handle any uncommitted changes."""
        print("\n🔍 STEP 2: Handle Uncommitted Changes")
        print("=" * 70)
        
        status = self.run("git status --porcelain", silent=True).stdout.strip()
        
        if not status:
            print("✅ Working directory is clean")
            return
        
        print("\n⚠️  Found uncommitted changes:")
        print(status)
        
        print("\n🤔 What to do?")
        print("   1. Commit them (recommended)")
        print("   2. Stash them")
        print("   3. Discard them")
        
        choice = input("\nChoose (1/2/3): ").strip()
        
        if choice == "1":
            # Get list of files, skip Interview Question Bank
            files = []
            for line in status.split('\n'):
                if line and "Interview Question Bank" not in line:
                    filename = line[3:].strip()
                    files.append(filename)
            
            for f in files:
                self.run(f'git add "{f}"', check=False)
            
            self.run('git commit -m "chore: commit changes before v4.0 reorganization"')
            print("✅ Changes committed")
            
        elif choice == "2":
            self.run('git stash push -u -m "Before v4.0 reorganization"')
            print("✅ Changes stashed (restore with: git stash pop)")
            
        elif choice == "3":
            confirm = input("\n⚠️  DISCARD changes? Type 'yes': ")
            if confirm.lower() == "yes":
                self.run("git reset --hard HEAD")
                self.run("git clean -fd")
                print("✅ Changes discarded")
            else:
                sys.exit(0)
        else:
            sys.exit(0)
    
    def create_backup(self):
        """Create backup."""
        print("\n💾 STEP 3: Create Backup")
        print("=" * 70)
        
        self.run("git branch -f master-backup-v3 master")
        self.run("git tag -f v3.0.0-archive master", check=False)
        print("✅ Backup created: master-backup-v3")
    
    def create_individual_branches(self):
        """Create SEPARATE branch for each feature."""
        print("\n🌳 STEP 4: Create Individual Feature Branches")
        print("=" * 70)
        print("\nℹ️  Each branch shows ONLY that feature's commits\n")
        
        for feature in self.features:
            print(f"\n{'='*70}")
            print(f"📌 {feature['branch']}")
            print(f"   {feature['description']}")
            print(f"{'='*70}")
            
            # Create branch from base commit
            print(f"   Starting from commit: {feature['base_commit'][:7]}")
            self.run(f"git checkout -b {feature['branch']} {feature['base_commit']}")
            
            # Cherry-pick ONLY this feature's commits
            if feature['commits']:
                for commit in feature['commits']:
                    print(f"   📥 Adding commit {commit[:7]}...")
                    result = self.run(f"git cherry-pick {commit}", check=False, silent=True)
                    if result.returncode != 0:
                        print(f"      ℹ️  Skipping (already applied or conflict)")
                        self.run("git cherry-pick --abort", check=False, silent=True)
            
            # Add any additional files for this feature
            if feature['files']:
                files_added = []
                for file in feature['files']:
                    if Path(file).exists():
                        self.run(f'git add "{file}"', check=False)
                        files_added.append(file)
                
                if files_added:
                    commit_msg = f"feat: add {', '.join([f.split('/')[-1] for f in files_added])}"
                    self.run(f'git commit -m "{commit_msg}"', check=False)
                    print(f"   ✅ Added files: {', '.join(files_added)}")
            
            # Count commits in this branch
            commit_count = self.run(
                f"git rev-list --count {feature['base_commit']}..{feature['branch']}", 
                silent=True
            ).stdout.strip()
            
            print(f"\n   ✅ Branch created: {commit_count} commit(s) in this feature")
        
        # Return to master
        self.run("git checkout master")
    
    def create_main_v4(self):
        """Tag current master as v4.0.0."""
        print("\n🎯 STEP 5: Create v4.0.0 Release")
        print("=" * 70)
        
        self.run("git checkout master")
        
        tag_message = "v4.0.0 - Modular Feature Branches\\n\\nEach feature has its own isolated branch showing incremental development"
        self.run(f'git tag -a v{self.version} -m "{tag_message}"')
        
        print(f"✅ Tagged master as v{self.version}")
    
    def show_summary(self):
        """Show final summary."""
        print("\n" + "=" * 70)
        print("✅ INDIVIDUAL FEATURE BRANCHES CREATED - v4.0.0")
        print("=" * 70)
        
        print("\n📊 Feature Branches (Each Separate):")
        print()
        
        for feature in self.features:
            # Count commits in this specific branch
            result = self.run(
                f"git rev-list --count {feature['base_commit']}..{feature['branch']}", 
                silent=True
            )
            count = result.stdout.strip() if result.returncode == 0 else "?"
            
            print(f"  {feature['branch']}")
            print(f"    → {feature['description']}")
            print(f"    → {count} commit(s) in this feature")
            print()
        
        print("=" * 70)
        print("\n🎯 How to Use:")
        
        print("\n1️⃣  View a specific feature:")
        print("   git checkout feature/research-agent")
        print("   git log --oneline")
        print("   # Shows ONLY research agent commits!")
        
        print("\n2️⃣  Compare features:")
        print("   git checkout feature/clarity-agent")
        print("   # See only ClarityAgent work")
        print("   git checkout feature/validator-agent")
        print("   # See only ValidatorAgent work")
        
        print("\n3️⃣  Push all branches:")
        print("   git remote add origin <your-repo-url>")
        print("   git push -u origin master")
        print("   git push --all origin")
        print("   git push --tags")
        
        print("\n4️⃣  Show branch structure:")
        print("   git log --all --graph --oneline --simplify-by-decoration")
        
        print("\n💡 Portfolio Benefit:")
        print("   - Each branch = focused demo of one feature")
        print("   - No clutter from other features")
        print("   - Easy to showcase individual work")
        print("   - Clean, professional presentation")
        
        print("\n🛡️  Safety: master-backup-v3")

def main():
    """Run the reorganization."""
    
    print("=" * 70)
    print("🚀 INDIVIDUAL FEATURE BRANCHES - v4.0.0")
    print("=" * 70)
    print("\nCreates SEPARATE branches for each feature:")
    print("  - Each branch shows ONLY that feature's commits")
    print("  - No cumulative build-up")
    print("  - Perfect for portfolio showcase")
    print()
    print("Example:")
    print("  feature/research-agent → ONLY research agent commit")
    print("  feature/validator-agent → ONLY validator commit")
    
    confirm = input("\n🤔 Ready? (yes/no): ")
    if confirm.lower() not in ["yes", "y"]:
        print("❌ Cancelled.")
        return 0
    
    organizer = IndividualFeatureBranches()
    
    try:
        organizer.update_gitignore()
        organizer.handle_uncommitted_changes()
        organizer.create_backup()
        organizer.create_individual_branches()
        organizer.create_main_v4()
        organizer.show_summary()
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Individual feature branches ready")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted! Restoring...")
        subprocess.run("git checkout master", shell=True)
        subprocess.run("git reset --hard master-backup-v3", shell=True)
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())