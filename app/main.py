"""
main.py

This is the main entry point for the application. It orchestrates the scheduling, generation,
and updating of all dynamic content, including commit messages, weather summaries, time progress
charts, Bing images, geo wonders, and journal entries. It also manages git operations to keep
the repository and README up to date.

Key features:
- Initializes the database and git repository on startup.
- Schedules and runs all generator modules at configurable intervals.
- Handles copying generated files (README, SVGs) into the repository.
- Commits and pushes changes to the remote git repository, with support for force-push and history cleanup.
- Provides robust logging and error handling for all major operations.
- Supports both continuous operation and a test mode for single-cycle runs.
- Aggregates and updates UI state for presentation.

Typical usage:
- Run as the main process to keep the repository and README in sync with generated content.
- Can be run in test mode for development and debugging.

Dependencies:
- app.generators.* (for all content generators)
- app.services.* (for data and utility services)
- app.data.* (for database and repository operations)
- app.presentation.ui_state (for UI state aggregation)
- app.config (for configuration and logger setup)
- Python standard library (asyncio, shutil, os, datetime, typing, pathlib)
"""

import asyncio
import shutil
import os
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path

from app.generators.commit_gen import generate_commit_messages
from app.generators.time_gen import generate_time_message
from app.generators.weather_gen import generate_weather_message
from app.generators.bing_gen import generate_bing_message
from app.generators.geo_gen import generate_geo_message
from app.generators.journal_gen import generate_journal_message

from app.services.weather import get_weather
from app.services.time import get_time_info
from app.data.database_init import init_database as init_db
from app.presentation.ui_state import state

from app.config import (
    REPO_DIR,
    README_PATH,
    COMMIT_MSG_PATH,
    TIME_DARK_SVG_PATH,
    TIME_LIGHT_SVG_PATH,

    GITHUB_USERNAME, 
    GITHUB_API_KEY,
    REMOTE_URL,

    TIME_MESSAGE_INTERVAL, 
    WEATHER_COMMIT_INTERVAL,
    BING_MESSAGE_INTERVAL,
    GEO_MESSAGE_TIME,
    GEO_MESSAGE_HOUR,
    GEO_MESSAGE_MINUTE,
    JOURNAL_MESSAGE_TIME,
    JOURNAL_MESSAGE_HOUR,
    JOURNAL_MESSAGE_MINUTE,

    MAX_COMMITS_BEFORE_REBASE,
    DEFAULT_BRANCH,

    FORCE_PUSH_ON_STARTUP,
    FORCE_PUSH_SCHEDULE_HOUR,
    FORCE_PUSH_SCHEDULE_MINUTE
    )

from app.config import setup_logger

logger = setup_logger("main", indent=0)

logger.debug(f"COMMIT_MSG_PATH exists: {COMMIT_MSG_PATH.exists()}")
logger.debug(f"README exists: {README_PATH.exists()}")
logger.debug(f"DARK SVG exists: {TIME_DARK_SVG_PATH.exists()}")
logger.debug(f"LIGHT SVG exists: {TIME_LIGHT_SVG_PATH.exists()}")
logger.debug(f"REPO_DIR: {REPO_DIR}, exists: {REPO_DIR.exists()}")

async def run_git_command(command: list, cwd: Path = None) -> tuple[bool, str, str]:
    """
    Run a git command asynchronously.
    
    Args:
        command: List of command parts
        cwd: Working directory (defaults to REPO_DIR)
        
    Returns:
        Tuple of (success, stdout, stderr)
    """
    if cwd is None:
        cwd = REPO_DIR
    
    try:
        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        success = process.returncode == 0
        stdout_str = stdout.decode('utf-8').strip()
        stderr_str = stderr.decode('utf-8').strip()
        
        if success:
            logger.debug(f"Git command successful: {' '.join(command)}")
        else:
            logger.error(f"Git command failed: {' '.join(command)}, stderr: {stderr_str}")
        
        return success, stdout_str, stderr_str
        
    except Exception as e:
        logger.error(f"Error running git command {' '.join(command)}: {e}")
        return False, "", str(e)


async def initialize_git_repo():
    """Initialize git repository if it doesn't exist."""
    if not REPO_DIR.exists():
        logger.error(f"Repository directory {REPO_DIR} does not exist")
        return False
    
    git_dir = REPO_DIR / ".git"
    
    if not git_dir.exists():
        logger.info("Initializing Git repository...")
        
        # Initialize repo
        success, _, _ = await run_git_command(["git", "init"])
        if not success:
            return False
        
        # Add remote
        success, _, _ = await run_git_command(["git", "remote", "add", "origin", REMOTE_URL])
        if not success:
            return False
        
        # Create and switch to branch
        success, _, _ = await run_git_command(["git", "checkout", "-b", DEFAULT_BRANCH])
        if not success:
            return False
        
        logger.info("Git repository initialized successfully")
    else:
        logger.debug("Git repository already exists")
        
        # Ensure we're on the correct branch
        success, _, _ = await run_git_command(["git", "checkout", DEFAULT_BRANCH])
        if not success:
            # Try to create the branch if it doesn't exist
            success, _, _ = await run_git_command(["git", "checkout", "-b", DEFAULT_BRANCH])
    
    return True


async def copy_files_to_repo():
    """Copy generated files to the repository."""
    try:
        files_copied = []
        
        # Debug: Log what paths we're checking
        logger.debug(f"Checking README_PATH: {README_PATH} (exists: {README_PATH.exists()})")
        logger.debug(f"Checking TIME_DARK_SVG_PATH: {TIME_DARK_SVG_PATH} (exists: {TIME_DARK_SVG_PATH.exists()})")
        logger.debug(f"Checking TIME_LIGHT_SVG_PATH: {TIME_LIGHT_SVG_PATH} (exists: {TIME_LIGHT_SVG_PATH.exists()})")
        logger.debug(f"Target REPO_DIR: {REPO_DIR} (exists: {REPO_DIR.exists()})")
        
        # Copy README from presentation/ui
        if README_PATH.exists():
            shutil.copy2(README_PATH, REPO_DIR / "README.md")
            files_copied.append("README.md")
            logger.debug(f"Copied {README_PATH} to {REPO_DIR / 'README.md'}")
        else:
            logger.warning(f"README file not found at {README_PATH}")
        
        # Copy time dark SVG
        if TIME_DARK_SVG_PATH.exists():
            shutil.copy2(TIME_DARK_SVG_PATH, REPO_DIR / "time-dark.svg")
            files_copied.append("time-dark.svg")
            logger.debug(f"Copied {TIME_DARK_SVG_PATH} to {REPO_DIR / 'time-dark.svg'}")
        else:
            logger.warning(f"Time dark SVG not found at {TIME_DARK_SVG_PATH}")
        
        # Copy time light SVG
        if TIME_LIGHT_SVG_PATH.exists():
            shutil.copy2(TIME_LIGHT_SVG_PATH, REPO_DIR / "time-light.svg")
            files_copied.append("time-light.svg")
            logger.debug(f"Copied {TIME_LIGHT_SVG_PATH} to {REPO_DIR / 'time-light.svg'}")
        else:
            logger.warning(f"Time light SVG not found at {TIME_LIGHT_SVG_PATH}")

        if files_copied:
            logger.info(f"Copied to repository: {', '.join(files_copied)}")
        else:
            logger.warning("No files found to copy - check your file paths in config")
        
        return len(files_copied) > 0  # Return True only if files were actually copied
    except Exception as e:
        logger.error(f"Error copying files to repository: {e}")
        return False


async def get_commit_count() -> int:
    """Get the current number of commits in the repository."""
    success, stdout, _ = await run_git_command(["git", "rev-list", "--count", "HEAD"])
    if success and stdout:
        try:
            return int(stdout)
        except ValueError:
            logger.error(f"Invalid commit count output: {stdout}")
    return 0


async def force_push_repository():
    """
    Force push the current repository state to remote.
    This will overwrite the remote repository history.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.warning("Starting force push operation...")
        
        # Ensure we have the latest local changes
        if not await copy_files_to_repo():
            logger.error("Failed to copy files before force push")
            return False
        
        # Add all changes
        success, _, _ = await run_git_command(["git", "add", "."])
        if not success:
            logger.error("Failed to add files for force push")
            return False
        
        # Check if there are changes to commit
        success, stdout, _ = await run_git_command(["git", "status", "--porcelain"])
        if success and stdout.strip():
            # Commit if there are changes
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            commit_msg = f"[{timestamp}] 🚀 Force push update"
            
            success, _, _ = await run_git_command(["git", "commit", "-m", commit_msg])
            if not success:
                logger.error("Failed to commit changes before force push")
                return False
        
        # Force push
        push_url = f"https://{GITHUB_USERNAME}:{GITHUB_API_KEY}@github.com/{GITHUB_USERNAME}/obsidian-memo.git"
        success, _, stderr = await run_git_command(["git", "push", "-f", push_url, DEFAULT_BRANCH])
        
        if success:
            logger.info("🚀 Repository force pushed successfully!")
            return True
        else:
            logger.error(f"Force push failed: {stderr}")
            return False
            
    except Exception as e:
        logger.error(f"Error during force push: {e}")
        return False


async def cleanup_commit_history():
    """
    Clean up commit history by creating a new orphan branch and force pushing.
    This removes all commit history while keeping the current state.
    """
    logger.info("Starting commit history cleanup...")
    
    try:
        # Create a new orphan branch
        temp_branch = f"temp-cleanup-{int(datetime.now().timestamp())}"
        success, _, _ = await run_git_command(["git", "checkout", "--orphan", temp_branch])
        if not success:
            return False
        
        # Add all files
        success, _, _ = await run_git_command(["git", "add", "."])
        if not success:
            return False
        
        # Create initial commit
        success, _, _ = await run_git_command([
            "git", "commit", "-m", "🧹 History cleanup - fresh start"
        ])
        if not success:
            return False
        
        # Delete old main branch
        success, _, _ = await run_git_command(["git", "branch", "-D", DEFAULT_BRANCH])
        if not success:
            logger.warning("Could not delete old main branch")
        
        # Rename temp branch to main
        success, _, _ = await run_git_command(["git", "branch", "-m", DEFAULT_BRANCH])
        if not success:
            return False
        
        # Force push to update remote
        push_url = f"https://{GITHUB_USERNAME}:{GITHUB_API_KEY}@github.com/{GITHUB_USERNAME}/obsidian-memo.git"
        success, _, _ = await run_git_command(["git", "push", "-f", push_url, DEFAULT_BRANCH])
        if not success:
            return False
        
        logger.info("✨ Commit history cleanup completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error during commit history cleanup: {e}")
        return False


async def commit_and_push_changes(timeout: int = 10, force_push: bool = False):
    """
    Commit and push changes to the repository.
    
    Args:
        timeout: Timeout in seconds for the entire operation (default: 10)
        force_push: Whether to force push changes (default: False)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        async with asyncio.timeout(timeout):
            # Check if there are changes to commit
            success, stdout, _ = await run_git_command(["git", "status", "--porcelain"])
            if not success:
                return False
            
            if not stdout.strip():
                logger.debug("No changes to commit")
                return True
            
            # Copy files to repository
            if not await copy_files_to_repo():
                return False
            
            # Read commit message
            commit_msg = "🤖 Automated update"
            if COMMIT_MSG_PATH.exists():
                try:
                    with open(COMMIT_MSG_PATH, 'r', encoding='utf-8') as f:
                        commit_msg = f.read().strip()
                except Exception as e:
                    logger.warning(f"Could not read commit message from {COMMIT_MSG_PATH}: {e}")
            
            # Add all changes
            success, _, _ = await run_git_command(["git", "add", "."])
            if not success:
                return False
            
            # Commit changes
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            full_commit_msg = f"[{timestamp}] {commit_msg}"

            
            success, _, _ = await run_git_command(["git", "commit", "-m", full_commit_msg])
            if not success:
                logger.debug("Nothing to commit (possibly no changes)")
                return True
                    
            # Check if we need to cleanup history
            commit_count = await get_commit_count()
            if commit_count >= MAX_COMMITS_BEFORE_REBASE:
                logger.info(f"Reached {commit_count} commits, cleaning up history...")
                return await cleanup_commit_history()
            
            # Push changes
            push_url = f"https://{GITHUB_USERNAME}:{GITHUB_API_KEY}@github.com/{GITHUB_USERNAME}/obsidian-memo.git"
            push_command = ["git", "push"]
            if force_push:
                push_command.append("-f")
                logger.warning("Force pushing changes - this will overwrite remote history!")
            push_command.extend([push_url, DEFAULT_BRANCH])
            
            success, _, stderr = await run_git_command(push_command)
            
            if success:
                push_type = "force pushed" if force_push else "pushed"
                logger.info(f"✨ Changes committed and {push_type} successfully (commit #{commit_count + 1})")
                return True
            else:
                logger.error(f"Failed to push changes: {stderr}")
                return False
                
    except asyncio.TimeoutError:
        logger.error(f"Git operations timed out after {timeout} seconds")
        return False
    except Exception as e:
        logger.error(f"Error in commit_and_push_changes: {e}")
        return False

async def wait_until_next_minute() -> None:
    """
    Wait until the next minute boundary (0 seconds).
    
    This ensures that all scheduled tasks run at precise minute intervals.
    """
    now = datetime.now()
    next_minute = now.replace(second=0, microsecond=0) + timedelta(minutes=1)
    wait_seconds = (next_minute - now).total_seconds()
    logger.debug(f"Waiting {wait_seconds:.2f} seconds until next minute")
    await asyncio.sleep(wait_seconds)
    await asyncio.sleep(0.5)


def should_run_weather_commit(now: datetime) -> bool:
    """
    Check if weather and commit messages should be generated.
    
    Args:
        now: Current datetime
        
    Returns:
        True if current time is at a 15-minute quarter (00, 15, 30, 45)
    """
    return now.minute % WEATHER_COMMIT_INTERVAL == 0


def should_run_bing(now: datetime) -> bool:
    """
    Check if bing message should be generated.
    
    Args:
        now: Current datetime
        
    Returns:
        True if current time is at the top of an hour (minute 00)
    """
    return now.minute == 0


def should_run_geo(now: datetime, last_geo_date: Optional[datetime]) -> bool:
    """
    Check if geo message should be generated.
    
    Args:
        now: Current datetime
        last_geo_date: Last date when geo message was generated
        
    Returns:
        True if it's 10:00 and geo hasn't run today
    """
    if now.hour != GEO_MESSAGE_HOUR or now.minute != GEO_MESSAGE_MINUTE:
        return False
    
    if last_geo_date is None:
        return True
        
    # Check if it hasn't run today
    return last_geo_date.date() < now.date()


def should_run_journal(now: datetime, last_journal_date: Optional[datetime]) -> bool:
    """
    Check if journal message should be generated.
    
    Args:
        now: Current datetime
        last_journal_date: Last date when journal message was generated
        
    Returns:
        True if it's the scheduled time and journal hasn't run today
    """
    if now.hour != JOURNAL_MESSAGE_HOUR or now.minute != JOURNAL_MESSAGE_MINUTE:
        return False
    
    if last_journal_date is None:
        return True
        
    # Check if it hasn't run today
    return last_journal_date.date() < now.date()


def should_run_force_push(now: datetime, last_force_push_date: Optional[datetime]) -> bool:
    """
    Check if scheduled force push should run.
    
    Args:
        now: Current datetime
        last_force_push_date: Last date when force push was executed
        
    Returns:
        True if it's the scheduled time and force push hasn't run today
    """
    if FORCE_PUSH_SCHEDULE_HOUR is None or FORCE_PUSH_SCHEDULE_MINUTE is None:
        return False
        
    if now.hour != FORCE_PUSH_SCHEDULE_HOUR or now.minute != FORCE_PUSH_SCHEDULE_MINUTE:
        return False
    
    if last_force_push_date is None:
        return True
        
    # Check if it hasn't run today
    return last_force_push_date.date() < now.date()


async def generate_messages_safely(tasks: list, task_names: list) -> None:
    """
    Execute message generation tasks with error handling.
    
    Args:
        tasks: List of coroutine tasks to execute
        task_names: List of task names for logging
    """
    try:
        logger.info(f"Starting generation of: {', '.join(task_names)}")
        await asyncio.gather(*tasks)
        logger.info(f"Successfully completed: {', '.join(task_names)}")
    except Exception as e:
        logger.error(f"Error generating messages ({', '.join(task_names)}): {e}", exc_info=True)
        raise


async def update_ui_safely() -> None:
    """Update UI with error handling."""
    try:
        await state.update_ui()
        logger.debug("UI updated successfully")
    except Exception as e:
        logger.error(f"Error updating UI: {e}", exc_info=True)
        # Don't re-raise - UI update failure shouldn't stop the main loop


async def single_updater(test: bool = False) -> None:
    """
    Main update loop that runs message generation and git operations on schedule.
    """
    logger.info("Starting update loop with git integration")
    last_geo_date: Optional[datetime] = None
    last_journal_date: Optional[datetime] = None
    last_force_push_date: Optional[datetime] = None

    while True:
        try:
            if test:
                logger.info(f"Loop iteration starting at {datetime.now()}")

            await wait_until_next_minute()
            await asyncio.sleep(1)

            now = datetime.now()
            try:
                if now.minute % 15 == 0:
                    os.system('clear')
            except:
                logger.error("Failed to clear the console")

            logger.debug(f"Processing update at {now}")

            tasks = []
            task_names = []

            # Always generate time message
            try:
                time_progress = get_time_info()
                tasks.append(generate_time_message(time_progress))
                task_names.append("time")
            except Exception as e:
                logger.error(f"Error getting time info: {e}", exc_info=True)
                continue

            # Weather and commit messages
            if should_run_weather_commit(now):
                try:
                    weather_data = await get_weather()
                    tasks.extend([
                        generate_weather_message(weather_data),
                        generate_commit_messages(weather_data)
                    ])
                    task_names.extend(["weather", "commit"])
                    logger.info("Scheduled weather and commit message generation")
                except Exception as e:
                    logger.error(f"Error getting weather data: {e}", exc_info=True)

            # Bing message
            if should_run_bing(now):
                tasks.append(generate_bing_message())
                task_names.append("bing")
                logger.info("Scheduled bing message generation")

            # Geo message
            if should_run_geo(now, last_geo_date):
                tasks.append(generate_geo_message())
                task_names.append("geo")
                last_geo_date = now
                logger.info("Scheduled geo message generation")

            # Journal message
            if should_run_journal(now, last_journal_date):
                tasks.append(generate_journal_message())
                task_names.append("journal")
                last_journal_date = now
                logger.info("Scheduled journal message generation")

            # Generate all messages
            if tasks:
                await generate_messages_safely(tasks, task_names)

            # ✅ UI update
            await update_ui_safely()

            # ✅ Copy files to repo
            if not await copy_files_to_repo():
                logger.warning("Copying files to repo failed, skipping commit")
                continue

            # Check for scheduled force push
            if should_run_force_push(now, last_force_push_date):
                logger.info("Executing scheduled force push...")
                force_push_success = await force_push_repository()
                if force_push_success:
                    last_force_push_date = now
                    logger.info("Scheduled force push completed successfully")
                else:
                    logger.error("Scheduled force push failed")
                continue  # Skip regular commit/push after force push

            # ✅ Commit and push (regular)
            git_success = await commit_and_push_changes()
            if not git_success:
                logger.warning("Git operations failed, but continuing...")

            if test:
                commit_count = await get_commit_count()
                logger.info(f"Completed update cycle. Commit count: {commit_count}")
                logger.info(f"Current commit: {getattr(state, 'commit_msg', 'N/A')}")

        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
            break
        except Exception as e:
            logger.error(f"Unexpected error in update loop: {e}", exc_info=True)
            await asyncio.sleep(5)


async def main() -> None:
    """
    Main entry point for the application.
    
    Initializes the database, git repository, and starts the update loop.
    """
    try:
        logger.info("Initializing README updater with git integration")
        
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")
        
        # Initialize git repository
        if not await initialize_git_repo():
            raise RuntimeError("Failed to initialize git repository")
        logger.info("Git repository initialized successfully")
        
        # Optional startup force push
        if FORCE_PUSH_ON_STARTUP:
            logger.info("Executing startup force push...")
            startup_force_push_success = await force_push_repository()
            if startup_force_push_success:
                logger.info("Startup force push completed successfully")
            else:
                logger.warning("Startup force push failed, continuing anyway...")
        
        print("🚀 README Updater with Git Integration started. Press Ctrl+C to stop.")
        print(f"📅 Schedule:")
        print(f"   • Time messages: Every {TIME_MESSAGE_INTERVAL} minute(s)")
        print(f"   • Weather/Commit: Every {WEATHER_COMMIT_INTERVAL} minutes (quarters)")
        print(f"   • Bing messages: Every {BING_MESSAGE_INTERVAL} minutes (hourly)")
        print(f"   • Geo messages: Daily at {GEO_MESSAGE_TIME}")
        print(f"   • Journal messages: Daily at {JOURNAL_MESSAGE_TIME}")
        print(f"   • Git commit/push: Every minute")
        print(f"   • History cleanup: Every {MAX_COMMITS_BEFORE_REBASE} commits")
        if FORCE_PUSH_SCHEDULE_HOUR is not None and FORCE_PUSH_SCHEDULE_MINUTE is not None:
            print(f"   • Force push: Daily at {FORCE_PUSH_SCHEDULE_HOUR:02d}:{FORCE_PUSH_SCHEDULE_MINUTE:02d}")
        if FORCE_PUSH_ON_STARTUP:
            print(f"   • Startup force push: Enabled")
        
        await single_updater(test=True)
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
        print("\n👋 README Updater stopped.")
    except Exception as e:
        logger.error(f"Fatal error in main: {e}", exc_info=True)
        print(f"❌ Fatal error: {e}")
        raise


async def test_main() -> None:
    """
    Test function that runs one cycle of each message generator and tests git operations.
    
    Useful for testing the system without running the full scheduler.
    """
    print("=== Testing Main Function with Git ===")
    logger.info("Starting test mode")
    
    try:
        
        # Initialize database
        await init_db()
        logger.info("✓ Database initialized")
        
        # Initialize git
        if await initialize_git_repo():
            logger.info("✓ Git repository initialized")
        else:
            logger.error("✗ Git repository initialization failed")
        
        # Get data
        logger.info("Fetching data...")
        time_info = get_time_info()
        weather_data = await get_weather()
        logger.info("✓ Data fetched successfully")
        
        # Generate all message types
        logger.info("Generating all message types...")
        await asyncio.gather(
            generate_time_message(time_info),
            generate_weather_message(weather_data),
            generate_commit_messages(weather_data),
            generate_bing_message(),
            generate_geo_message(),
            generate_journal_message()
        )
        logger.info("✓ All messages generated successfully")
        
        # Update UI
        await state.update_ui()
        logger.info("✓ UI updated successfully")

        logger.info("=== Test is completed ===")
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        print(f"✗ Test failed: {e}")
        raise


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        asyncio.run(test_main())
    else:
        asyncio.run(main())