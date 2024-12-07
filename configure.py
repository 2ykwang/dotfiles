import os
import subprocess
 
BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def set_git_config(key, value):
    if value:
        subprocess.run(["git", "config", "--global", key, value], check=True)
        print(f"{GREEN}Set {key} to '{value}'{RESET}")
    else:
        print(f"{YELLOW}Skipped setting {key} (no value){RESET}")

def prompt_user_input(prompt_message, default_value=None):
    prompt_message = f"{BLUE}{prompt_message}"
    if default_value:
        prompt_message += f" [{default_value}]: {RESET}"
    else:
        prompt_message += f": {RESET}"
    
    user_input = input(prompt_message).strip()
    return user_input if user_input else default_value

def main(): 
    print(f"{BLUE}Configuring git user settings...{RESET}")
 
    git_username = prompt_user_input("Enter your Git username")
    git_email = prompt_user_input("Enter your Git email")

    set_git_config("core.editor", "vim")
    set_git_config("gpg.program", "/opt/homebrew/bin/gpg")
    set_git_config("commit.gpgsign", "true")
    set_git_config("tag.gpgsign", "true")
    set_git_config("init.defaultBranch", "main")

    set_git_config("user.name", git_username)
    set_git_config("user.email", git_email)

    print(f"{GREEN}User configuration completed.{RESET}")

if __name__ == "__main__":
    main()
