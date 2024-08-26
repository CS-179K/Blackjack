# **Blackjack**

By Mario Martinez (mmart477), Ocean Chen (ochen011), Ted Voo (tvoo001), Alec Boghossian (aleclb223) 
<sub>(Github Username/Account)<sub>

## **Project Idea**
A blackjack simulator designed to help blackjack enthusiasts or new players interested in learning the game by providing a digital environment where users can practice and refine blackjack skills. The simulator replicates real-life blackjack games, allowing the user to play multiple hands, practice card counting, and master basic strategy without committing real money.

## **Installation Instruction**
Installation Instructions for Linux:<br>
1. Open terminal, and run command sudo apt install git // this is to install git
2. Run command git clone https://github.com/CS-179K/Blackjack.git, Path to Blackjack Folder
3. Run command sudo apt install python-pip // This is to install pip
4. Run command pip install -r requirements.txt
5. Run commmad sudo apt install python3-flask
6. Run command flask --app Game --debug run
7. Click on the link in terminal

Installation Instructions for Window:<br>
1. Install Git from their website https://git-scm.com/book/en/v2/Getting-Started-Installing-Git
2. Clone the git repository with git clone https://github.com/CS-179K/Blackjack.git
3. Download and install Python from https://www.python.org/downloads/ // Latest Verision, Remember to check the box to add python to PATH during installation
4. Verify pip is install by running command pip --version in the command prompt
5. Run command pip install -r requirements.txt
6. Run commmad pip show flask //if flask is not installed, install it with pip install flask
7. Run command flask --app Game --debug run
8. Click on the link in command prompt

Installation Instructions for macOS:<br>
1. Install Homebrew via this command in terminal /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
2. Install Git via this command in terminal brew install git
3. Clone git repository via this command git clone https://github.com/CS-179K/Blackjack.git
4. Path to the Blackjack Folder in terminal via cd
5. Verify that python is installed on device with command python3 --version
6. Install pip with command sudo easy_install pip
7. Run the command pip3 install -r requirements.txt
8. Run the command pip3 show flask
9. Run the command flask --app Game --debug run
10. Access the application via the link in terminal output

## **Usage Instructions**
Option 1: Start a game of blackjack directly from the home screen.
Option 2: Explore various game modes such as Card Counting Practice, Standard Game, or Basic Strategy Training.

Each game mode features buttons for actions like Hit, Stay, Double, Insurance, Surrender, and specific betting options.
To save your high scores, bankroll, wins, and total games played, consider creating an account. Registering will allow you to log in and continue your progress seamlessly!

## **Details**
**Major Functional Features**
1. Blackjack Game Rules (Story Points: 8) 
2. Basic Strategy Gamemode (Story Points: 7) 
3. Standard 3/2 Blackjack Gamemode (Story Points: 5)
4. Statistical Analysis and Reporting (Story Points: 5)
5. Card Counting Gamemode (Story Points: 4)
6. Login/Register User Accounts (Story Points: 3) 
7. Bankroll (Credit) Management (Story Points: 3)
8. Card Dealing Animations (Story Points: 3)

**Non-Functional Features**
1. Performance and Speed
2. Scalability
3. Reliability and Uptime
4. Security and Privacy
5. User Interface Usability
6. Cross-Platform Compatibility
8. Resource Efficiency
9. Support and Documentation

**Techniques**
1. Programming Languages: C/C++/Python
2. Web Development Tools: HTML/CSS/JS
3. JavaScript Frameworks and Environments: React/Node.js
4. Database Query Language: SQL

**Architecture**

![Diagram](https://github.com/CS-179K/Blackjack/blob/main/Lab_files/Blackjack.drawio.png?raw=true)


## **Card Values**
A - 11 or 1  
2 to 9 - Just their numeric values  
10, J, Q, K - 10 

